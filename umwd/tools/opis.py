#!/usr/bin/env python3
"""Renderer części opisowej – tekst Markdown z placeholderami modelu → HTML → PDF (Chromium) + podglądy PNG + zeszyt.

Etap II (R-116, Wyj. 21 odp. 88 = S-04): maks. 5 stron A3 tekstu, czcionka min. 11 pkt → A3 poziomo (420×297 mm), 3 łamy.
Etap I  (R-071, R-072, Wyj. 14 odp. 66): maks. 5 stron A4 tekstu (11 pkt), załączniki poza limitem → A4 pionowo, 1 łam;
         wszystko po znaczniku <!-- ANNEX --> to załącznik (osobny skład, osobne liczenie stron).

Wejście (pisane przez innych autorów):  docs/95_opis/etap2_opis.md, docs/95_opis/etap1_opis.md
Fixture'y testowe:                       docs/95_opis/_test/*.md     (tryb --test → build/opis/_test/)
Wyjście:   build/opis/opis_etap2_A3.{html,pdf}       build/opis/opis_etap1_A4.{html,pdf} (+ opis_etap1_A4_zal.html)
           build/opis/podglad/<nazwa>-<n>.png (~1600 px)   build/opis/<nazwa>_kontrola.json (strony, wypełnienie, czcionki)
Zeszyt:    --zeszyt        → build/opis/CZESC_OPISOWA.pdf        = tekst Etapu II + F.15.A + F.15.B + F.15.C + F.14.B + plansze A3
           --zeszyt-etap1  → build/opis/etap1/CZESC_OPISOWA.pdf  = tekst Etapu I (+ zał.) + F.14.A + plansze A3
           Metadane PDF neutralne (R-082, R-127, R-133): brak Author/Creator/Producer/dat i XMP; brak numeru identyfikacyjnego.

Składnia (kontrakt z autorami tekstu):
  # / ## / ### nagłówki, akapity, listy (-, *, 1.), **pogrubienie**, *kursywa*, proste tabele z kreskami |, ![podpis](plik)
  {{K:ścieżka|fmt}} – model/koncepcja.json, {{B:ścieżka|fmt}} – model/budynek.json; ścieżka: segmenty po '.', element listy
  przez indeks (bryly.0) albo selektor [klucz=wartość] (bryly[id=W]); fmt: liczba miejsc po przecinku (0–6; przecinek
  dziesiętny, wąska twarda spacja U+202F jako separator tysięcy od 10 000, liczby 4-cyfrowe bez separatora, minus U+2212)
  albo raw (tekst bez zmian; liczba bez zaokrąglenia w zapisie polskim). Brak |fmt = raw.
  Nierozwiązana ścieżka = BŁĄD (plik:wiersz, ścieżka, powód) – nigdy pusta wartość.
  Komentarze HTML są usuwane z wydruku. Znaczniki: <!-- ANNEX -->, <!-- PAGEBREAK -->, <!-- COLBREAK -->,
  <!-- SPAN --> (następny blok na pełną szerokość strony), <!-- LEDGER: wartość | znaczenie | źródło --> (rejestr liczb
  wpisanych dosłownie; kontrola „liczby spoza LEDGER” w raporcie).

Użycie:
  tools/opis.py                         # składa oba etapy, jeśli istnieją pliki .md
  tools/opis.py --etap 2 [--src PLIK.md] [--out KATALOG] [--bez-podgladu]
  tools/opis.py --check PLIK.md [...]   # tylko placeholdery + LEDGER (szybko, bez składu)
  tools/opis.py --zeszyt [--allow-missing]      tools/opis.py --zeszyt-etap1 [--allow-missing]
  tools/opis.py --test                  # fixture'y docs/95_opis/_test + testy negatywne
Kody wyjścia: 0 OK · 1 błąd placeholdera/składni · 2 przekroczony limit stron · 3 brak elementu zeszytu · 4 błąd składu/kontroli.
Uruchamia się w /home/user/aihouse/.venv-render (pypdf, pymupdf, pyphen, PIL) – przy innym interpreterze przełącza się sam.
"""
from __future__ import annotations

import argparse
import hashlib
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import time
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT.parent / ".venv-render"
HTML2PDF = ROOT / "tools" / "plansze" / "html2pdf.js"
MODELS = {"K": ROOT / "model" / "koncepcja.json", "B": ROOT / "model" / "budynek.json"}
OUT = ROOT / "build" / "opis"
SRC_DIR = ROOT / "docs" / "95_opis"
TEST_DIR = SRC_DIR / "_test"

try:  # spójność z planszami (src/umwd/board.py)
    sys.path.insert(0, str(ROOT / "src"))
    from umwd.board import ACC, INK  # noqa: E402
except Exception:  # noqa: BLE001
    ACC, INK = "#a8483a", "#1d1b18"
GREY, RULE = "#57524b", "#cfcac2"

NNBSP, NBSP, SHY, MINUS = " ", " ", "­", "−"
S0, S1 = "", ""           # wartownik placeholdera w tekście (prywatny obszar Unicode)

# ------------------------------------------------------------------------------------------------ typografia / layout
# Jedyne źródło rozmiarów czcionek w CSS (sprawdzane: min ≥ 11 pt, R-072 / R-116).
FONT_PT = {"body": 11.0, "table": 11.0, "caption": 11.0, "list": 11.0, "header": 11.0, "h3": 11.0, "h2": 14.0,
           "h1": 18.0, "title": 26.0}
LEADING = 1.32
MIN_PT = 11.0
# Chromium/HarfBuzz zapisuje rozmiar kroju w stałym przecinku 26.6 px (1/64 px) z obcięciem w dół: 11 pt = 14,667 px →
# 14,656 px = 10,99 pt w PDF. Do CSS trafia rozmiar nominalny + 0,01 pt, żeby w PDF było ≥ 11,00 pt (sprawdzane z PDF).
PT_COMP = 0.01
TITLE = "Budynek administracyjny Urzędu Marszałkowskiego Województwa Dolnośląskiego we Wrocławiu – część opisowa"

LAYOUTS = {
    # w, h [mm]; marginesy [mm]: góra (z paskiem nagłówka), dół, lewy, prawy; łamy, odstęp łamów
    "A3": dict(w=420.0, h=297.0, top=24.0, bottom=14.0, left=18.0, right=18.0, cols=3, gap=9.0),
    "A4": dict(w=210.0, h=297.0, top=27.0, bottom=16.0, left=31.0, right=29.0, cols=1, gap=8.0),   # łam 150 mm ≈ 75–80 zn.
    "A4zal": dict(w=210.0, h=297.0, top=27.0, bottom=16.0, left=18.0, right=18.0, cols=1, gap=8.0),
}
STAGES = {
    2: dict(src="etap2_opis.md", name="opis_etap2_A3", layout="A3", limit=5, label="Etap II",
            header=[f"{TITLE}, Etap II"]),
    1: dict(src="etap1_opis.md", name="opis_etap1_A4", layout="A4", limit=5, label="Etap I",
            header=["Budynek administracyjny Urzędu Marszałkowskiego Województwa",
                    "Dolnośląskiego we Wrocławiu – część opisowa, Etap I"]),
}
assert min(FONT_PT.values()) >= MIN_PT, "rozmiar czcionki poniżej 11 pt"


class OpisError(Exception):
    code = 4


class PlaceholderError(OpisError):
    code = 1

    def __init__(self, errors):
        self.errors = errors
        super().__init__("\n".join(errors))


class ResolveError(Exception):
    pass


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------ liczby
def fmt_number(v, dec):
    """Zapis polski: przecinek dziesiętny, U+202F co 3 cyfry od 10 000 (4 cyfry bez separatora), minus U+2212.
    dec=None → bez zaokrąglania (raw); zaokrąglanie połówkowe w górę od zapisu dziesiętnego (repr), nie binarnego."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ResolveError(f"wartość nie jest liczbą ({type(v).__name__})")
    d = Decimal(repr(v)) if isinstance(v, float) else Decimal(v)
    if not d.is_finite():
        raise ResolveError(f"wartość nieskończona/NaN ({v!r})")
    if dec is not None:
        d = d.quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    neg = d < 0
    s = format(abs(d), "f")
    ip, _, fp = s.partition(".")
    if len(ip) >= 5:
        g = []
        while len(ip) > 3:
            g.insert(0, ip[-3:])
            ip = ip[:-3]
        ip = NNBSP.join([ip] + g)
    out = ip + ("," + fp if fp else "")
    return MINUS + out if neg else out


# ------------------------------------------------------------------------------------------------ modele i ścieżki
def load_models():
    data, meta = {}, {}
    for k, p in MODELS.items():
        raw = None
        for attempt in range(5):           # koncepcja.json bywa właśnie zapisywana przez inny proces
            try:
                raw = p.read_bytes()
                data[k] = json.loads(raw.decode("utf-8"))
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                if attempt == 4:
                    raise OpisError(f"{p.relative_to(ROOT)}: niepoprawny JSON (plik w trakcie zapisu?)")
                time.sleep(1.0)
        m = data[k].get("meta", {}) if isinstance(data[k], dict) else {}
        meta[k] = {"plik": str(p.relative_to(ROOT)), "sha1": hashlib.sha1(raw).hexdigest()[:10],
                   "wersja": m.get("wersja") or m.get("wersja_specyfikacji")}
    return data, meta


def split_path(path):
    segs, buf, depth = [], [], 0
    for ch in path:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth < 0:
                raise ResolveError("nadmiarowy nawias ]")
        if ch == "." and depth == 0:
            segs.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if depth:
        raise ResolveError("niezamknięty nawias [")
    segs.append("".join(buf))
    return segs


SEG_RE = re.compile(r"^([^\[\]]*)((?:\[[^\[\]]*\])*)$")


def _same(a, v):
    v = v.strip().strip("'\"")
    if str(a) == v:
        return True
    if isinstance(a, (int, float)) and not isinstance(a, bool):
        try:
            return float(v) == float(a)
        except ValueError:
            return False
    return False


def _keys(d):
    ks = list(d)
    return ", ".join(map(str, ks[:15])) + (" …" if len(ks) > 15 else "")


def resolve_path(root, path):
    cur, trail = root, ""
    for seg in split_path(path.strip()):
        m = SEG_RE.match(seg)
        if not m or (m.group(1) == "" and not m.group(2)):
            raise ResolveError(f"pusty lub niepoprawny segment ścieżki „{seg}”")
        name, sels = m.group(1).strip(), re.findall(r"\[([^\[\]]*)\]", m.group(2))
        if name:
            if isinstance(cur, dict):
                if name not in cur:
                    raise ResolveError(f"brak klucza „{name}” w {trail or 'korzeniu'} (dostępne: {_keys(cur)})")
                cur = cur[name]
            elif isinstance(cur, list):
                if not re.fullmatch(r"-?\d+", name):
                    raise ResolveError(f"{trail} jest listą – użyj indeksu albo selektora [klucz=wartość], nie „{name}”")
                i = int(name)
                if not -len(cur) <= i < len(cur):
                    raise ResolveError(f"indeks {i} poza listą {trail} (długość {len(cur)})")
                cur = cur[i]
            else:
                raise ResolveError(f"{trail} to wartość ({type(cur).__name__}) – nie ma w niej „{name}”")
            trail = f"{trail}.{name}" if trail else name
        for sel in sels:
            if "=" in sel:
                k, v = (x.strip() for x in sel.split("=", 1))
                if not isinstance(cur, list):
                    raise ResolveError(f"selektor [{sel}] wymaga listy, a {trail} to {type(cur).__name__}")
                hits = [x for x in cur if isinstance(x, dict) and k in x and _same(x[k], v)]
                if not hits:
                    vals = [str(x.get(k)) for x in cur if isinstance(x, dict) and k in x]
                    raise ResolveError(f"brak elementu [{sel}] w {trail} (wartości „{k}”: "
                                       f"{', '.join(vals[:25]) or '—'}{' …' if len(vals) > 25 else ''})")
                if len(hits) > 1:
                    raise ResolveError(f"selektor [{sel}] niejednoznaczny w {trail} ({len(hits)} trafień)")
                cur = hits[0]
            elif isinstance(cur, list) and re.fullmatch(r"\s*-?\d+\s*", sel):
                i = int(sel)
                if not -len(cur) <= i < len(cur):
                    raise ResolveError(f"indeks [{i}] poza listą {trail} (długość {len(cur)})")
                cur = cur[i]
            elif isinstance(cur, dict) and sel in cur:
                cur = cur[sel]
            else:
                raise ResolveError(f"nie można zastosować [{sel}] do {trail}")
            trail += f"[{sel}]"
    return cur


def format_value(v, fmt):
    fmt = (fmt or "raw").strip()
    if v is None:
        raise ResolveError("wartość null w modelu")
    if fmt == "raw":
        if isinstance(v, str):
            return v
        if isinstance(v, bool):
            raise ResolveError("wartość logiczna (true/false) – nie do wstawienia w tekst")
        if isinstance(v, (int, float)):
            return fmt_number(v, None)
        raise ResolveError(f"wartość nie jest skalarem ({type(v).__name__}) – wskaż element dokładniej")
    if re.fullmatch(r"[0-6]", fmt):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ResolveError(f"wartość nie jest liczbą ({type(v).__name__}: {str(v)[:50]!r}) – dla tekstu użyj |raw")
        return fmt_number(v, int(fmt))
    raise ResolveError(f"nieznany format „{fmt}” (dozwolone: 0–6 albo raw)")


# ------------------------------------------------------------------------------------------------ wstępne przetwarzanie
COMMENT_RE = re.compile(r"<!--(.*?)-->", re.S)
MARKERS = ("ANNEX", "PAGEBREAK", "COLBREAK", "SPAN")
PH_RE = re.compile(r"\{\{(.*?)\}\}")
MARK_RE = re.compile(r"\x00([A-Z]+)\x00")


def strip_comments(text, fname):
    ledgers = []

    def repl(m):
        body = m.group(1)
        nl = body.count("\n")
        tag = body.strip().upper()
        first = tag.split(None, 1)[0].rstrip(":") if tag else ""
        if first == "LEDGER":
            ledgers.append((text.count("\n", 0, m.start()) + 1, body.strip()[len("LEDGER"):].lstrip(": \t")))
            return "\n" * nl
        if tag in MARKERS:
            return f"\x00{tag}\x00" + "\n" * nl
        return "\n" * nl

    out = COMMENT_RE.sub(repl, text)
    if "<!--" in out:
        ln = out[: out.index("<!--")].count("\n") + 1
        raise PlaceholderError([f"{fname}:{ln}: niezamknięty komentarz <!-- (brak -->)"])
    return out, ledgers


def parse_ledger(ledgers):
    entries = []
    for ln, body in ledgers:
        for i, line in enumerate(body.splitlines()):
            line = line.strip().lstrip("-*• ").strip()
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            entries.append({"wiersz": ln + i, "wartosc": parts[0], "znaczenie": parts[1] if len(parts) > 1 else "",
                            "zrodlo": " | ".join(parts[2:]) if len(parts) > 2 else ""})
    return entries


def resolve_placeholders(lines, fname, models):
    values, errors, used = [], [], []
    out = []
    for i, line in enumerate(lines, 1):
        def repl(m):
            inner = m.group(1)
            head, _, fmt = inner.partition("|")
            mm = re.fullmatch(r"\s*([A-Za-z]+)\s*:\s*(.+?)\s*", head)
            if not mm:
                errors.append(f"{fname}:{i}: niepoprawny placeholder „{{{{{inner}}}}}” (oczekiwano {{{{K:ścieżka|fmt}}}})")
                return ""
            src, path = mm.group(1), mm.group(2)
            if src not in models:
                errors.append(f"{fname}:{i}: nieznane źródło „{src}:” w „{{{{{inner}}}}}” (K = koncepcja.json, B = budynek.json)")
                return ""
            try:
                val = format_value(resolve_path(models[src], path), fmt)
            except ResolveError as e:
                errors.append(f"{fname}:{i}: nierozwiązana ścieżka {src}:{path} – {e}")
                return ""
            values.append(val)
            used.append({"wiersz": i, "zrodlo": src, "sciezka": path, "fmt": (fmt or "raw").strip(), "wartosc": val})
            return f"{S0}{len(values) - 1}{S1}"

        new = PH_RE.sub(repl, line)
        if "{{" in new or "}}" in new:
            errors.append(f"{fname}:{i}: niedomknięty lub uszkodzony placeholder: „{line.strip()[:120]}”")
        out.append(new)
    if errors:
        raise PlaceholderError(errors)
    return out, values, used


# ------------------------------------------------------------------------------------------------ inline
_PYPHEN = None


def hyphenator():
    global _PYPHEN
    if _PYPHEN is None:
        try:
            import pyphen
            _PYPHEN = pyphen.Pyphen(lang="pl_PL", left=2, right=3)
        except Exception:  # noqa: BLE001
            _PYPHEN = False
            log("UWAGA: brak pyphen – dzielenie wyrazów tylko przez CSS hyphens:auto (Chromium nie ma słownika pl)")
    return _PYPHEN


WORD_RE = re.compile(r"[^\W\d_]{6,}")


def hyphenate(s):
    h = hyphenator()
    if not h:
        return s
    return WORD_RE.sub(lambda m: m.group(0) if m.group(0).isupper() else h.inserted(m.group(0), hyphen=SHY), s)


ABBR = r"(?:ul|al|pl|nr|pkt|ok|tj|np|tzw|art|ust|poz|tab|rys|zał|str|s|r|godz|lit|wg|ok|ca|m\.in|§)"


def typo(s):
    s = s.replace("...", "…").replace(" -- ", f"{NBSP}– ").replace("--", "–")
    s = re.sub(r"\s+[-–]\s+", f"{NBSP}– ", s)                                 # półpauza, nie na początku wiersza
    s = re.sub(r'"([^"\n]+)"', "„\\1”", s)                                     # cudzysłów polski
    s = re.sub(r"(?<![\w­])([aiouwzAIOUWZ]) +", "\\1" + NBSP, s)          # sierotki: a i o u w z
    s = re.sub(rf"(?<![\w])({ABBR}\.?) +(?=[\w\d{S0}])", "\\1" + NBSP, s)      # ul. Mazowiecka, § 13, nr 5
    s = re.sub(rf"(?<=[\d{S1}]) (?=[^\s\d{S0}]{{1,6}}(?:[\s.,;:)!?]|$))", NBSP, s)   # 8,9 m · 150 mln · 26 %
    s = re.sub(r"(?<!\d)(\d{1,3})((?: \d{3})+)(?![\d])", lambda m: m.group(1) + m.group(2).replace(" ", NNBSP), s)
    s = re.sub(r" (n\.p\.m\.|p\.p\.t\.|zł\b|m²|m³)", NBSP + r"\1", s)                # 156,50 m n.p.m. · mln zł
    return s


BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
ITAL_RE = re.compile(r"(?<![\w*])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![\w*])")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_RE = re.compile(r"`([^`]+)`")
SENT_RE = re.compile(f"{S0}(\\d+){S1}")


class Ctx:
    def __init__(self, fname, values):
        self.fname, self.values, self.warnings = fname, values, []


def inline(s, ctx, hyph=True, ln=None):
    if LINK_RE.search(s):
        ctx.warnings.append(f"{ctx.fname}:{ln}: odnośnik zamieniony na sam tekst (bez adresów www – R-127)")
        s = LINK_RE.sub(r"\1", s)
    if "`" in s:
        s = CODE_RE.sub(r"\1", s)
    s = _html.escape(s, quote=False)
    s = typo(s)
    if hyph:
        s = hyphenate(s)
    s = BOLD_RE.sub(r"<strong>\1</strong>", s)
    s = ITAL_RE.sub(r"<em>\1</em>", s)
    return SENT_RE.sub(lambda m: _html.escape(ctx.values[int(m.group(1))], quote=False), s)


def plain(s, ctx):
    return SENT_RE.sub(lambda m: ctx.values[int(m.group(1))], s).replace("*", "")


# ------------------------------------------------------------------------------------------------ bloki
H_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
LI_RE = re.compile(r"^(\s*)([-*+•]|\d+[.)])\s+(.*)$")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
IMG_RE = re.compile(r"^\s*!\[(.*?)\]\((.*?)\)\s*$")
NUM_CELL_RE = re.compile(r"^[−\-+±≈~≤≥<>]?\s?\d[\d\s  .,]*\s?(%|‰|[A-Za-złąęóśćńżźŁ²³/.·°]{0,8})$")


def split_row(s):
    s = s.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def parse_blocks(lines, first_ln, ctx):
    """lines: wiersze po rozwiązaniu placeholderów; first_ln: numer pierwszego wiersza w pliku."""
    blocks, para, i = [], [], 0

    def flush():
        if para:
            blocks.append({"t": "p", "text": " ".join(x for x, _ in para).replace("\x01 ", "\x01"), "ln": para[0][1]})
            para.clear()

    while i < len(lines):
        ln = first_ln + i
        s = lines[i].rstrip("\n")
        marks = MARK_RE.findall(s)
        if marks:
            flush()
            for mk in marks:
                blocks.append({"t": "mark", "m": mk, "ln": ln})
            s = MARK_RE.sub("", s)
            if not s.strip():
                i += 1
                continue
        if not s.strip():
            flush()
            i += 1
            continue
        m = H_RE.match(s)
        if m:
            flush()
            lvl = len(m.group(1))
            if lvl > 3:
                ctx.warnings.append(f"{ctx.fname}:{ln}: nagłówek poziomu {lvl} składany jak ###")
                lvl = 3
            blocks.append({"t": "h", "lvl": lvl, "text": m.group(2), "ln": ln})
            i += 1
            continue
        if s.strip() in ("---", "***", "___"):
            flush()
            i += 1
            continue
        if s.lstrip().startswith("|") and i + 1 < len(lines) and SEP_RE.match(lines[i + 1]):
            flush()
            head = split_row(s)
            aligns = []
            for c in split_row(lines[i + 1]):
                c = c.strip()
                aligns.append("c" if c.startswith(":") and c.endswith(":") else "r" if c.endswith(":") else
                              "l" if c.startswith(":") else "")
            rows, j = [], i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                r = split_row(lines[j])
                if len(r) != len(head):
                    ctx.warnings.append(f"{ctx.fname}:{first_ln + j}: wiersz tabeli ma {len(r)} komórek zamiast {len(head)}")
                    r = (r + [""] * len(head))[: len(head)]
                rows.append(r)
                j += 1
            cap = None
            if blocks and blocks[-1]["t"] == "p" and re.match(r"^\**\s*(Tabela|Tab\.)", blocks[-1]["text"]) \
                    and len(blocks[-1]["text"]) < 240:
                cap = blocks.pop()["text"]
            blocks.append({"t": "table", "head": head, "aligns": (aligns + [""] * len(head))[: len(head)],
                           "rows": rows, "cap": cap, "ln": ln})
            i = j
            continue
        m = IMG_RE.match(s)
        if m:
            flush()
            blocks.append({"t": "img", "alt": m.group(1), "src": m.group(2), "ln": ln})
            i += 1
            continue
        m = LI_RE.match(s)
        if m:
            flush()
            items, j = [], i
            while j < len(lines):
                t = lines[j].rstrip("\n")
                if MARK_RE.search(t):
                    break
                mm = LI_RE.match(t)
                if mm:
                    items.append({"ind": len(mm.group(1).expandtabs(4)), "ord": mm.group(2)[0].isdigit(),
                                  "text": mm.group(3), "ln": first_ln + j})
                    j += 1
                    continue
                if t.strip() and t.startswith((" ", "\t")) and items and not H_RE.match(t.strip()):
                    items[-1]["text"] += " " + t.strip()     # kontynuacja pozycji
                    j += 1
                    continue
                break
            blocks.append({"t": "list", "items": items, "ln": ln})
            i = j
            continue
        hard = s.endswith("  ") or s.endswith("\\")
        para.append((s.rstrip(" \\").strip() + ("\x01" if hard else ""), ln))
        i += 1
    flush()
    return blocks


def render_list(items, ctx):
    out, stack = [], []          # stack: (indent, tag)
    for it in items:
        tag = "ol" if it["ord"] else "ul"
        while stack and it["ind"] < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or it["ind"] > stack[-1][0]:
            out.append(f"<{tag}>")
            stack.append((it["ind"], tag))
        else:
            out.append("</li>")
        out.append("<li>" + inline(it["text"], ctx, ln=it["ln"]))
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def render_blocks(blocks, ctx, src_dir, multicol):
    out, span_next, first = [], False, True
    for b in blocks:
        if b["t"] == "mark":
            if b["m"] == "PAGEBREAK":
                out.append('<div class="pb"></div>')
            elif b["m"] == "COLBREAK":
                out.append('<div class="cb"></div>')
            elif b["m"] == "SPAN":
                span_next = True
            continue
        cls = ["span"] if span_next else []
        span_next = False
        if b["t"] == "h":
            txt = inline(b["text"], ctx, hyph=False, ln=b["ln"])
            m = re.match(r"^((?:\d+\.)*\d+\.?|[A-Z]\.|[a-z]\))(\s|&nbsp;| )(.*)$", txt)
            if m and b["lvl"] >= 2:
                txt = f'<span class="k">{m.group(1)}</span> {m.group(3)}'
            if b["lvl"] == 1 and first:
                cls.append("title")
            c = f' class="{" ".join(cls)}"' if cls else ""
            out.append(f"<h{b['lvl']}{c}>{txt}</h{b['lvl']}>")
        elif b["t"] == "p":
            c = f' class="{" ".join(cls)}"' if cls else ""
            out.append(f"<p{c}>" + inline(b["text"], ctx, ln=b["ln"]).replace("\x01", "<br>") + "</p>")
        elif b["t"] == "list":
            h = render_list(b["items"], ctx)
            out.append(h if not cls else f'<div class="span">{h}</div>')
        elif b["t"] == "table":
            n = len(b["rows"])
            cls.append("small" if n <= 14 else "long")
            rows_html = []
            aligns = list(b["aligns"])
            for k, a in enumerate(aligns):          # wyrównanie automatyczne: kolumna liczbowa → do prawej
                if not a:
                    col = [plain(r[k], ctx).strip() for r in b["rows"] if r[k].strip()]
                    aligns[k] = "r" if col and all(NUM_CELL_RE.match(x) for x in col) else ""
            th = "".join(f'<th{" class=" + chr(34) + a + chr(34) if a else ""}>{inline(h, ctx, hyph=False, ln=b["ln"])}</th>'
                         for h, a in zip(b["head"], aligns))
            for r in b["rows"]:
                rows_html.append("<tr>" + "".join(
                    f'<td{" class=" + chr(34) + a + chr(34) if a else ""}>{inline(c, ctx, hyph=(a != "r"), ln=b["ln"])}</td>'
                    for c, a in zip(r, aligns)) + "</tr>")
            cap = f"<caption>{inline(b['cap'], ctx, hyph=False, ln=b['ln'])}</caption>" if b["cap"] else ""
            out.append(f'<table class="{" ".join(cls)}">{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(rows_html)}</tbody></table>')
        elif b["t"] == "img":
            p = (src_dir / b["src"]).resolve()
            if not p.exists():
                raise PlaceholderError([f"{ctx.fname}:{b['ln']}: brak pliku ilustracji {b['src']}"])
            c = f' class="{" ".join(cls)}"' if cls else ""
            cap = f"<figcaption>{inline(b['alt'], ctx, ln=b['ln'])}</figcaption>" if b["alt"] else ""
            out.append(f'<figure{c}><img src="{p.as_uri()}" alt="">{cap}</figure>')
        first = False
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ kontrola liczb dosłownych
LIT_RE = re.compile(r"(?<![\w.,\-/:§­])(\d{1,3}(?:[   ]\d{3})+|\d+)(?:,\d+)?(?![\w\-]|[.:]\d|­)")


def norm_num(s):
    return re.sub(r"[\s  ]", "", s).replace(MINUS, "-")


def literal_numbers(lines, first_ln, ledger):
    known = set()
    for e in ledger:
        for t in re.findall(r"\d[\d\s  ]*(?:[,.]\d+)?", e["wartosc"]):
            known.add(norm_num(t.strip()).replace(".", ","))
    found = []
    for k, line in enumerate(lines):
        s = MARK_RE.sub("", line)
        s = SENT_RE.sub(" ", s)
        if SEP_RE.match(s):
            continue
        s = re.sub(r"^\s*#{1,6}\s+[\dA-Za-z]+(?:\.\d+)*[.)]?\s", " ", s)   # numeracja nagłówka
        s = re.sub(r"^\s*\d+[.)]\s", " ", s)                               # numeracja listy
        s = re.sub(r"\b\d+(?:\.\d+)+\b", " ", s)                          # 7.1, 17.11.2026 – identyfikatory/daty
        s = re.sub(r"\b(?:Tabela|Tab\.|Rys\.|rys\.|Plansza|plansza|Wyj\.|odp\.|Etap|etap)\s*[A-Z]?\d+", " ", s)  # numeracja
        for m in LIT_RE.finditer(s):
            tok = m.group(0)
            if norm_num(tok) not in known:
                found.append({"wiersz": first_ln + k, "liczba": tok.replace(NNBSP, " ").replace(NBSP, " "),
                              "kontekst": s[max(0, m.start() - 30): m.end() + 30].strip()})
    return found


# ------------------------------------------------------------------------------------------------ czcionki
# Chromium (Skia) osadza kroje OpenType-CFF (.otf) jako Type 3 – słabsza jakość druku/podglądu i brak nazw kroju.
# Dlatego potrzebne odmiany Inter / Inter Display (te same co na planszach, /usr/share/fonts/opentype/inter) są
# konwertowane do konturów TrueType (fontTools cu2qu, max_err 1 jedn./em) i ładowane przez @font-face → CID TrueType.
FONT_DIR = Path("/usr/share/fonts/opentype/inter")
FONT_FACES = [("Inter", 400, "normal", "Inter-Regular"), ("Inter", 400, "italic", "Inter-Italic"),
              ("Inter", 600, "normal", "Inter-SemiBold"), ("Inter", 600, "italic", "Inter-SemiBoldItalic"),
              ("Inter Display", 300, "normal", "InterDisplay-Light"), ("Inter Display", 400, "normal", "InterDisplay-Regular"),
              ("Inter Display", 500, "normal", "InterDisplay-Medium"), ("Inter Display", 600, "normal", "InterDisplay-SemiBold")]


def otf_to_ttf(src, dst):
    from fontTools.pens.cu2quPen import Cu2QuPen
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from fontTools.ttLib import TTFont, newTable
    f = TTFont(str(src))
    order = f.getGlyphOrder()
    gs = f.getGlyphSet()
    glyphs = {}
    for g in order:
        pen = TTGlyphPen(gs)
        gs[g].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
        glyphs[g] = pen.glyph()
    f["loca"] = newTable("loca")
    f["glyf"] = glyf = newTable("glyf")
    glyf.glyphOrder, glyf.glyphs = order, glyphs
    del f["CFF "]
    if "VORG" in f:
        del f["VORG"]
    glyf.compile(f)
    hmtx = f["hmtx"]
    for g, gl in glyf.glyphs.items():
        if hasattr(gl, "xMin"):
            hmtx[g] = (hmtx[g][0], gl.xMin)
    f["maxp"] = maxp = newTable("maxp")
    maxp.tableVersion = 0x00010000
    for k in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
              "maxStackElements", "maxSizeOfInstructions"):
        setattr(maxp, k, 1 if k == "maxZones" else 0)
    maxp.maxComponentElements = max(len(getattr(g, "components", []) or []) for g in glyf.glyphs.values())
    maxp.compile(f)
    post = f["post"]
    post.formatType, post.extraNames, post.mapping, post.glyphOrder = 2.0, [], {}, order
    try:
        post.compile(f)
    except OverflowError:
        post.formatType = 3.0
    f.sfntVersion = "\x00\x01\x00\x00"
    tmp = dst.with_suffix(".tmp")
    f.save(str(tmp))
    tmp.replace(dst)


def font_faces(outdir):
    """@font-face dla TrueType-owych kopii Inter (pamięć podręczna build/opis/_fonts); bez fontTools → kroje systemowe."""
    fd = OUT / "_fonts"
    fd.mkdir(parents=True, exist_ok=True)
    css = []
    for fam, wt, style, stem in FONT_FACES:
        src = FONT_DIR / f"{stem}.otf"
        dst = fd / f"{stem}.ttf"
        if not src.exists():
            log(f"UWAGA: brak {src} – kroje systemowe")
            return ""
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            try:
                otf_to_ttf(src, dst)
            except Exception as e:  # noqa: BLE001
                log(f"UWAGA: konwersja {src.name} → TTF nie powiodła się ({e}); kroje systemowe (Type 3 w PDF)")
                return ""
        css.append(f"@font-face {{ font-family: '{fam}'; font-weight: {wt}; font-style: {style}; "
                   f"src: url('{dst.as_uri()}') format('truetype'); }}")
    return "\n".join(css)


# ------------------------------------------------------------------------------------------------ CSS / HTML
def css_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def make_css(lay, header_lines, page_label):
    L = LAYOUTS[lay]
    f = {k: round(v + PT_COMP, 2) for k, v in FONT_PT.items()}
    head = css_str("\n".join(header_lines)).replace("\n", "\\A ")
    box = (f"font-family: 'Inter', 'DejaVu Sans', sans-serif; font-size: {f['header']}pt; line-height: 1.22; "
           f"vertical-align: bottom; padding-bottom: 2.4mm; margin-bottom: 6.5mm; border-bottom: 0.3mm solid {INK};")
    multicol = L["cols"] > 1
    return f"""
@page {{
  size: {L['w']}mm {L['h']}mm;
  margin: {L['top']}mm {L['right']}mm {L['bottom']}mm {L['left']}mm;
  @top-left {{ content: {head}; white-space: pre; color: {GREY}; font-weight: 400; text-align: left; {box} }}
  @top-right {{ content: {css_str(page_label)} counter(page) "/" counter(pages); white-space: pre; color: {ACC};
               font-weight: 600; text-align: right; {box} }}
}}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; background: #fff; color: {INK}; font-family: 'Inter', 'DejaVu Sans', sans-serif;
       font-size: {f['body']}pt; line-height: {LEADING}; font-feature-settings: 'ss01' 1, 'kern' 1; font-kerning: normal; }}
main.flow {{ {f"column-count: {L['cols']}; column-gap: {L['gap']}mm; column-rule: 0.2mm solid #d9d3ca; column-fill: balance;" if multicol else ""}
       text-align: justify; hyphens: auto; -webkit-hyphens: auto; orphans: 2; widows: 2; }}
p {{ margin: 0 0 1.9mm 0; text-wrap: pretty; }}
strong {{ font-weight: 600; }}
em {{ font-style: italic; }}
h1, h2, h3 {{ text-align: left; hyphens: manual; break-after: avoid; break-inside: avoid; text-wrap: balance; }}
h1 {{ font-family: 'Inter Display', 'Inter', sans-serif; font-weight: 400; font-size: {f['h1']}pt; line-height: 1.12;
      letter-spacing: -0.1pt; margin: 6mm 0 3mm 0; }}
h1.title {{ column-span: all; font-weight: 300; font-size: {f['title']}pt; line-height: 1.06; letter-spacing: -0.3pt;
      margin: 0 0 6mm 0; padding-bottom: 3.2mm; border-bottom: 0.6mm solid {INK}; }}
h2 {{ font-family: 'Inter Display', 'Inter', sans-serif; font-weight: 500; font-size: {f['h2']}pt; line-height: 1.18;
      letter-spacing: 0.05pt; margin: 5.2mm 0 2.2mm 0; }}
h2 .k, h3 .k {{ color: {ACC}; font-weight: 600; }}
h3 {{ font-weight: 600; font-size: {f['h3']}pt; line-height: {LEADING}; margin: 3.4mm 0 1.1mm 0; }}
h1:first-child, h2:first-child, h3:first-child {{ margin-top: 0; }}
ul, ol {{ margin: 0 0 1.9mm 0; padding-left: 4.6mm; font-size: {f['list']}pt; }}
ul {{ list-style: none; }}
ul > li {{ position: relative; }}
ul > li::before {{ content: "–"; position: absolute; left: -4.6mm; color: {ACC}; }}
ol {{ padding-left: 6mm; }}
ol > li::marker {{ color: {ACC}; font-weight: 600; }}
li {{ margin: 0 0 0.7mm 0; text-wrap: pretty; }}
li > ul, li > ol {{ margin: 0.7mm 0 0 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 1.2mm 0 3.2mm 0; font-size: {f['table']}pt; line-height: 1.25;
         text-align: left; hyphens: manual; }}
table.small {{ break-inside: avoid; }}
caption {{ caption-side: top; text-align: left; font-weight: 600; font-size: {f['caption']}pt; line-height: 1.25;
           padding: 0 0 1.4mm 0; break-after: avoid; }}
th {{ font-weight: 600; border-bottom: 0.35mm solid {INK}; padding: 0.8mm 3mm 0.9mm 0; vertical-align: bottom; }}
td {{ border-bottom: 0.2mm solid {RULE}; padding: 0.8mm 3mm 0.8mm 0; vertical-align: top; }}
th:last-child, td:last-child {{ padding-right: 0; }}
td.r, th.r {{ text-align: right; white-space: nowrap; }}
td.r {{ font-variant-numeric: tabular-nums; }}
td.c, th.c {{ text-align: center; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
figure {{ margin: 1.2mm 0 3.2mm 0; break-inside: avoid; }}
figure img {{ display: block; width: 100%; }}
figcaption {{ font-size: {f['caption']}pt; color: {GREY}; line-height: 1.25; margin-top: 1.2mm; text-align: left; }}
.span {{ column-span: all; }}
.pb {{ break-before: page; height: 0; margin: 0; }}
.cb {{ break-before: column; height: 0; margin: 0; }}
"""


def css_min_font(css):
    """Najmniejszy nominalny rozmiar czcionki zadeklarowany w CSS (pt, bez kompensacji PT_COMP) – kontrola statyczna."""
    sizes = [round(float(x) - PT_COMP, 2) for x in re.findall(r"font-size:\s*([\d.]+)pt", css)]
    bad = re.findall(r"font-size:\s*[\d.]+(?:px|em|rem|%)|font:\s", css)
    if bad:
        raise OpisError(f"CSS zawiera rozmiary czcionek spoza pt: {bad}")
    return min(sizes), sorted(set(sizes))


def html_doc(body, lay, header_lines, page_label, title):
    css = font_faces(OUT) + "\n" + make_css(lay, header_lines, page_label)
    return (f'<!doctype html>\n<html lang="pl"><head><meta charset="utf-8"><title>{_html.escape(title)}</title>'
            f"<style>{css}</style></head>\n<body><main class=\"flow\">\n{body}\n</main></body></html>\n"), css


# ------------------------------------------------------------------------------------------------ PDF
def run_html2pdf(html_path, pdf_path, lay):
    if not shutil.which("node"):
        raise OpisError("brak node – silnik PDF tools/plansze/html2pdf.js wymaga Node + Playwright")
    L = LAYOUTS[lay]
    p = subprocess.run(["node", str(HTML2PDF), str(html_path), str(pdf_path), f"{L['w']}", f"{L['h']}", "--outline"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    if p.returncode != 0 or not pdf_path.exists():
        raise OpisError(f"html2pdf.js nie powiodło się: {p.stderr[-800:]}")


def neutral_writer(writer, title):
    writer.metadata = None
    writer.add_metadata({"/Title": title})
    try:
        writer.xmp_metadata = None
    except Exception:  # noqa: BLE001
        pass
    root = writer._root_object
    for k in ("/Metadata", "/PieceInfo"):
        if k in root:
            del root[k]
    for pg in writer.pages:
        for k in ("/Metadata", "/PieceInfo"):
            if k in pg:
                del pg[k]


def neutralize_pdf(src, dst, title):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(clone_from=PdfReader(str(src)))
    neutral_writer(w, title)
    tmp = dst.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as fh:
        w.write(fh)
    tmp.replace(dst)


def check_metadata(pdf):
    from pypdf import PdfReader
    r = PdfReader(str(pdf))
    md = {k: str(v) for k, v in (r.metadata or {}).items()}
    xmp = "/Metadata" in r.trailer["/Root"]
    leaks = [k for k in md if k not in ("/Title",)]
    return {"metadane": md, "xmp": xmp, "ok": not leaks and not xmp}


def analyze_pdf(pdf, lay):
    """Strony, format, czcionki (rozmiar/nazwa z PDF), wypełnienie łamów, przepełnienia, średnia długość wiersza."""
    import pymupdf
    L = LAYOUTS[lay]
    k = 72 / 25.4
    top, bot = L["top"] * k, (L["h"] - L["bottom"]) * k
    bh = bot - top
    cw = (L["w"] - L["left"] - L["right"] - (L["cols"] - 1) * L["gap"]) / L["cols"]
    cols = [((L["left"] + c * (cw + L["gap"])) * k, (L["left"] + c * (cw + L["gap"]) + cw) * k) for c in range(L["cols"])]
    doc = pymupdf.open(str(pdf))
    rep = {"strony": doc.page_count, "format_mm": [], "min_pt": 99.0, "max_pt": 0.0, "czcionki": {},
           "zastepcze": [], "wypelnienie": [], "przepelnienia": [], "znaki_w_wierszu": None}
    cpl = []
    for pi, page in enumerate(doc):
        rep["format_mm"].append([round(page.rect.width / k, 1), round(page.rect.height / k, 1)])
        fill = [0.0] * len(cols)
        d = page.get_text("dict")
        for blk in d["blocks"]:
            for line in blk.get("lines", []):
                txt = "".join(s["text"] for s in line["spans"]).strip()
                if not txt:
                    continue
                x0, y0, x1, y1 = line["bbox"]
                for s in line["spans"]:
                    if not s["text"].strip():
                        continue
                    rep["min_pt"] = min(rep["min_pt"], s["size"])
                    rep["max_pt"] = max(rep["max_pt"], s["size"])
                    fn = s["font"].split("+")[-1]
                    rep["czcionki"][fn] = rep["czcionki"].get(fn, 0) + len(s["text"])
                    if not fn.lower().startswith("inter"):
                        rep["zastepcze"].append({"strona": pi + 1, "czcionka": fn, "tekst": s["text"][:40]})
                if y1 <= top + 1:          # pasek nagłówka
                    continue
                if y1 > bot + 2:
                    rep["przepelnienia"].append({"strona": pi + 1, "typ": "pod polem tekstu", "tekst": txt[:60]})
                hit = [c for c, (a, b) in enumerate(cols) if x1 > a + 1 and x0 < b - 1]
                if not hit:
                    continue
                home = min(hit, key=lambda c: abs((x0 + x1) / 2 - (cols[c][0] + cols[c][1]) / 2))
                spans_all = (x1 - x0) > (cw * k + L["gap"] * k * 0.5)
                for c in (hit if spans_all else [home]):
                    fill[c] = max(fill[c], min(1.0, (y1 - top) / bh))
                if not spans_all and x1 > cols[home][1] + 2.5:
                    rep["przepelnienia"].append({"strona": pi + 1, "typ": f"poza łam {home + 1}",
                                                 "o_mm": round((x1 - cols[home][1]) / k, 1), "tekst": txt[:60]})
                sz = max(s["size"] for s in line["spans"])
                if abs(sz - FONT_PT["body"]) < 0.05 and (x1 - x0) > 0.9 * cw * k and not spans_all:
                    cpl.append(len(txt.replace(SHY, "")))
        rep["wypelnienie"].append([round(x, 3) for x in fill])
    rep["min_pt"] = round(rep["min_pt"], 2) if rep["min_pt"] < 99 else None
    rep["max_pt"] = round(rep["max_pt"], 2)
    if cpl:
        cpl.sort()
        rep["znaki_w_wierszu"] = cpl[len(cpl) // 2]
    last = rep["wypelnienie"][-1] if rep["wypelnienie"] else [0]
    rep["wypelnienie_ostatniej"] = round(sum(last) / len(last), 3)
    rep["zastepcze"] = rep["zastepcze"][:20]
    doc.close()
    return rep


def previews(pdf, name, outdir):
    pd = outdir / "podglad"
    pd.mkdir(parents=True, exist_ok=True)
    for old in pd.glob(f"{name}-*.png"):
        old.unlink()
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-scale-to-x", "1600", "-scale-to-y", "-1", str(pdf), str(pd / name)],
                       check=True, capture_output=True)
    else:
        import pymupdf
        doc = pymupdf.open(str(pdf))
        for i, page in enumerate(doc, 1):
            page.get_pixmap(matrix=pymupdf.Matrix(1600 / page.rect.width, 1600 / page.rect.width)).save(
                str(pd / f"{name}-{i}.png"))
    return sorted(pd.glob(f"{name}-*.png"), key=lambda p: int(re.search(r"-(\d+)\.png$", p.name).group(1)))


# ------------------------------------------------------------------------------------------------ dokument
def parse_document(src, models):
    fname = str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src)
    text = src.read_text(encoding="utf-8").replace("\r\n", "\n")
    text, ledgers = strip_comments(text, fname)
    lines = text.split("\n")
    rlines, values, used = resolve_placeholders(lines, fname, models)
    ledger = parse_ledger(ledgers)
    ctx = Ctx(fname, values)
    cut = next((k for k, l in enumerate(rlines) if "\x00ANNEX\x00" in l), None)
    main_l, annex_l = (rlines, []) if cut is None else (rlines[:cut], rlines[cut:])
    if cut is not None:
        annex_l[0] = annex_l[0].replace("\x00ANNEX\x00", "")
    doc = {"fname": fname, "ctx": ctx, "values": values, "used": used, "ledger": ledger,
           "main": parse_blocks(main_l, 1, ctx), "annex": parse_blocks(annex_l, (cut or 0) + 1, ctx) if cut is not None else [],
           "literal": literal_numbers(rlines, 1, ledger), "annex_line": None if cut is None else cut + 1}
    return doc


def render_stage(stage, src, outdir, png=True, quiet=False):
    """Zwraca raport (dict). Wyjątek PlaceholderError → kod 1; raport['kod'] = 2 przy przekroczeniu limitu stron."""
    st = STAGES[stage]
    models, mmeta = load_models()
    doc = parse_document(src, models)
    ctx = doc["ctx"]
    outdir.mkdir(parents=True, exist_ok=True)
    tmpd = outdir / "_tmp"
    tmpd.mkdir(exist_ok=True)
    name = st["name"]
    parts = [("tekst", doc["main"], st["layout"], st["header"], "strona ", name)]
    if doc["annex"]:
        if stage == 2:
            ctx.warnings.append(f"{doc['fname']}:{doc['annex_line']}: <!-- ANNEX --> w Etapie II – R-116 przewiduje "
                                f"poza tekstem tylko F.15.A–C, F.14.B i plansze A3")
        hdr = st["header"][:-1] + [st["header"][-1] + " – załącznik"]
        parts.append(("zalacznik", doc["annex"], "A4zal" if st["layout"] == "A4" else st["layout"], hdr, "zał., strona ",
                      name + "_zal"))
    rep = {"etap": stage, "zrodlo": doc["fname"], "modele": mmeta, "placeholdery": len(doc["used"]),
           "ledger_pozycje": len(doc["ledger"]), "liczby_spoza_ledger": doc["literal"], "czesci": {}, "kod": 0}
    pdfs = []
    for key, blocks, lay, hdr, plabel, hname in parts:
        body = render_blocks(blocks, ctx, src.parent, LAYOUTS[lay]["cols"] > 1)
        title = f"Część opisowa – {st['label']}" + (" – załącznik" if key == "zalacznik" else "")
        h, css = html_doc(body, lay, hdr, plabel, title)
        hp = outdir / f"{hname}.html"
        hp.write_text(h, encoding="utf-8")
        tp = tmpd / f"{hname}.pdf"
        run_html2pdf(hp, tp, lay)
        a = analyze_pdf(tp, lay)
        a["css_min_pt"], a["css_rozmiary_pt"] = css_min_font(css)
        a["uklad"] = {kk: LAYOUTS[lay][kk] for kk in ("w", "h", "cols", "gap", "top", "bottom", "left", "right")}
        a["limit"] = st["limit"] if key == "tekst" else None
        rep["czesci"][key] = a
        pdfs.append((title, tp))
    out_pdf = outdir / f"{name}.pdf"
    if len(pdfs) == 1:
        neutralize_pdf(pdfs[0][1], out_pdf, pdfs[0][0])
    else:
        from pypdf import PdfWriter
        w = PdfWriter()
        for title, tp in pdfs:
            w.append(str(tp), outline_item=title)
        neutral_writer(w, f"Część opisowa – {st['label']}")
        with open(out_pdf, "wb") as fh:
            w.write(fh)
    shutil.rmtree(tmpd, ignore_errors=True)
    rep["pdf"] = str(out_pdf.relative_to(ROOT))
    rep["metadane"] = check_metadata(out_pdf)
    if png:
        rep["podglad"] = [str(p.relative_to(ROOT)) for p in previews(out_pdf, name, outdir)]
    rep["ostrzezenia"] = ctx.warnings
    # ---- werdykty
    t = rep["czesci"]["tekst"]
    L = LAYOUTS[st["layout"]]
    if t["strony"] > st["limit"]:
        rep["kod"] = 2
    bad_fmt = [f for part in rep["czesci"].values() for f in part["format_mm"]
               if abs(f[0] - LAYOUTS[part_l(part)]["w"]) > 0.6 or abs(f[1] - LAYOUTS[part_l(part)]["h"]) > 0.6]
    font_bad = any((p["min_pt"] or 0) < MIN_PT - 0.005 or p["css_min_pt"] < MIN_PT for p in rep["czesci"].values())
    if (bad_fmt or font_bad or any(p["przepelnienia"] for p in rep["czesci"].values())) and rep["kod"] == 0:
        rep["kod"] = 4
    (outdir / f"{name}_kontrola.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    if not quiet:
        summary(rep, st, L)
    return rep


def part_l(part):
    u = part["uklad"]
    for k, L in LAYOUTS.items():
        if all(L[x] == u[x] for x in u):
            return k
    return "A3"


def summary(rep, st, L):
    t = rep["czesci"]["tekst"]
    log(f"── {st['label']}: {rep['zrodlo']} → {rep['pdf']}")
    log(f"   modele: " + ", ".join(f"{m['plik']} [{m['wersja']}, sha1 {m['sha1']}]" for m in rep["modele"].values()))
    log(f"   placeholdery: {rep['placeholdery']} rozwiązanych · LEDGER: {rep['ledger_pozycje']} poz. · "
        f"liczby dosłowne spoza LEDGER: {len(rep['liczby_spoza_ledger'])}")
    flag = "OK" if t["strony"] <= st["limit"] else "PRZEKROCZONY LIMIT"
    log(f"   STRONY TEKSTU: {t['strony']} / limit {st['limit']} ({L['w']:.0f}×{L['h']:.0f} mm, łamy: {L['cols']}) – {flag}")
    log(f"   wypełnienie ostatniej strony: {t['wypelnienie_ostatniej'] * 100:.0f} % (łamy: "
        + ", ".join(f"{x * 100:.0f} %" for x in t["wypelnienie"][-1]) + ")")
    log(f"   czcionki: CSS min {t['css_min_pt']:g} pt {t['css_rozmiary_pt']}; PDF min {t['min_pt']} pt, max {t['max_pt']} pt; "
        f"kroje: {', '.join(sorted(t['czcionki']))}; znaków w wierszu (mediana): {t['znaki_w_wierszu']}")
    if "zalacznik" in rep["czesci"]:
        z = rep["czesci"]["zalacznik"]
        log(f"   ZAŁĄCZNIK (poza limitem, Wyj. 14 odp. 66): {z['strony']} str.; PDF min {z['min_pt']} pt")
    for p in rep["czesci"].values():
        for o in p["przepelnienia"][:8]:
            log(f"   PRZEPEŁNIENIE: {o}")
        for z in p["zastepcze"][:5]:
            log(f"   UWAGA czcionka zastępcza: {z}")
    for w in rep["ostrzezenia"][:20]:
        log(f"   UWAGA: {w}")
    if not rep["metadane"]["ok"]:
        log(f"   UWAGA metadane: {rep['metadane']}")
    if t["strony"] > st["limit"]:
        log(f"   ✖✖✖ BŁĄD: {t['strony']} stron > {st['limit']} (R-116/S-04 dla Etapu II, R-072 dla Etapu I) ✖✖✖")


# ------------------------------------------------------------------------------------------------ zeszyt
A3_PT = (420 / 25.4 * 72, 297 / 25.4 * 72)
A3_PX = (4961, 3508)


def board_numbers(stage):
    ns = set()
    for p in list((ROOT / "build" / "plansze").glob(f"etap{stage}_P*.pdf")) + list(
            (ROOT / "build" / "plansze").glob(f"etap{stage}_P*.png")):
        m = re.fullmatch(rf"etap{stage}_P(\d+)", p.stem)
        if m:
            ns.add(int(m.group(1)))
    eks = ROOT / "build" / "eksport" / ("" if stage == 2 else "etap1")
    for p in eks.glob("PLANSZA_*_A3.jpg"):
        ns.add(int(re.search(r"PLANSZA_(\d+)_A3", p.name).group(1)))
    return sorted(ns)


def board_a3(stage, n, cache, notes):
    """JPEG A3 300 dpi planszy n: build/eksport/…/PLANSZA_n_A3.jpg (gdy nie starszy niż PDF planszy) → rasteryzacja
    build/plansze/etapX_Pn.pdf w 300 dpi A3 → (ostatecznie) podgląd PNG przeskalowany."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    eks = ROOT / "build" / "eksport" / ("" if stage == 2 else "etap1") / f"PLANSZA_{n}_A3.jpg"
    bpdf = ROOT / "build" / "plansze" / f"etap{stage}_P{n}.pdf"
    bpng = ROOT / "build" / "plansze" / f"etap{stage}_P{n}.png"
    if eks.exists() and (not bpdf.exists() or eks.stat().st_mtime >= bpdf.stat().st_mtime - 1):
        sz = Image.open(eks).size
        notes.append(f"plansza {n}: {eks.relative_to(ROOT)} ({sz[0]}×{sz[1]} px)")
        if sz != A3_PX:
            notes.append(f"  UWAGA: wymiar {sz} ≠ {A3_PX} (A3 300 dpi)")
        return eks
    if eks.exists():
        notes.append(f"plansza {n}: {eks.relative_to(ROOT)} starszy niż {bpdf.name} – pominięty (nieaktualny eksport)")
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / f"etap{stage}_P{n}_A3.jpg"
    src = bpdf if bpdf.exists() else bpng if bpng.exists() else None
    if src is None:
        raise OpisError(f"brak planszy {n} Etapu {stage}")
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        notes.append(f"plansza {n}: {out.relative_to(ROOT)} (pamięć podręczna z {src.name})")
        return out
    if src.suffix == ".pdf" and shutil.which("pdftoppm"):
        base = cache / f"_r{stage}_{n}"
        subprocess.run(["pdftoppm", "-q", "-png", "-singlefile", "-scale-to-x", str(A3_PX[0]), "-scale-to-y", "-1",
                        "-aa", "yes", "-aaVector", "yes", str(src), str(base)], check=True)
        im = Image.open(str(base) + ".png").convert("RGB")
        Path(str(base) + ".png").unlink()
        how = f"rasteryzacja {src.name} (wektor) do A3 300 dpi"
    else:
        im = Image.open(src).convert("RGB")
        how = f"UWAGA: {src.name} {im.size[0]}×{im.size[1]} px przeskalowany do A3 (efektywnie ~{im.size[0] / 420 * 25.4:.0f} dpi)"
    s = min(A3_PX[0] / im.size[0], A3_PX[1] / im.size[1])
    if abs(s - 1) > 1e-3:
        im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    canvas = Image.new("RGB", A3_PX, (255, 255, 255))
    canvas.paste(im, ((A3_PX[0] - im.size[0]) // 2, (A3_PX[1] - im.size[1]) // 2))
    canvas.save(out, "JPEG", quality=92, subsampling=0, optimize=True, dpi=(300, 300))
    notes.append(f"plansza {n}: {how} → {out.relative_to(ROOT)}")
    return out


def images_pdf(jpgs, out):
    import pymupdf
    doc = pymupdf.open()
    for j in jpgs:
        page = doc.new_page(width=A3_PT[0], height=A3_PT[1])
        page.insert_image(page.rect, filename=str(j), keep_proportion=True)
    doc.save(str(out), garbage=3, deflate=True)
    doc.close()


def pdf_text_flags(pdf):
    import pymupdf
    d = pymupdf.open(str(pdf))
    txt = " ".join(p.get_text() for p in d)
    d.close()
    flags = []
    if re.search(r"robocz", txt, re.I):
        flags.append("zawiera słowo „robocza/roboczy” (wersja robocza?)")
    if re.search(r"\b\d{6}\b", txt):
        flags.append("zawiera liczbę 6-cyfrową – sprawdzić, czy to nie numer identyfikacyjny (R-133)")
    return flags


def build_zeszyt(stage, allow_missing, png=True, src=None, outdir=OUT):
    st = STAGES[stage]
    src = Path(src) if src else SRC_DIR / st["src"]
    if not src.exists():
        raise OpisError(f"brak {src} – zeszyt wymaga tekstu (fixture'y: --test)")
    rep = render_stage(stage, src, outdir, png=png)
    if rep["kod"] == 2:
        raise OpisError("tekst przekracza limit stron – zeszyt nie zostanie złożony")
    if rep["kod"]:
        raise OpisError(f"kontrola tekstu nie przeszła (kod {rep['kod']}) – zeszyt nie zostanie złożony")
    comps = [(f"Część opisowa – tekst ({st['label']})", outdir / f"{st['name']}.pdf")]
    tables = ["F.15.A", "F.15.B", "F.15.C", "F.14.B"] if stage == 2 else ["F.14.A"]
    names = {"F.15.A": "F.15.A – Tabela programowa", "F.15.B": "F.15.B – Zestawienie pomieszczeń",
             "F.15.C": "F.15.C – Dane bilansowe", "F.14.B": "F.14.B – Informacja o kosztach (Etap II)",
             "F.14.A": "F.14.A – Informacja o kosztach (Etap I)"}
    missing, notes = [], []
    newest_model = max(p.stat().st_mtime for p in MODELS.values())
    for code in tables:
        p = ROOT / "build" / "tabele" / f"{code}.pdf"
        if not p.exists():
            missing.append(f"{code} ({p.relative_to(ROOT)})")
            continue
        comps.append((names[code], p))
        if p.stat().st_mtime < newest_model:
            notes.append(f"UWAGA: {p.name} starszy niż model (koncepcja/budynek.json) – przegenerować tools/tabele_konkursowe.py?")
        for f in pdf_text_flags(p):
            notes.append(f"UWAGA: {p.name} {f}")
    ns = board_numbers(stage)
    exp = (1, 8) if stage == 2 else (2, 2)
    if not ns:
        missing.append(f"plansze Etapu {stage} (build/plansze/etap{stage}_P*.pdf|png, build/eksport/…_A3.jpg)")
    elif not exp[0] <= len(ns) <= exp[1]:
        notes.append(f"UWAGA: liczba plansz {len(ns)} (oczekiwano {exp[0]}–{exp[1]})")
    if missing and not allow_missing:
        for m in missing:
            log(f"   ✖ BRAK: {m}")
        e = OpisError("zeszyt niekompletny – brak elementów obowiązkowych (uruchom z --allow-missing dla wersji roboczej)")
        e.code = 3
        raise e
    zdir = outdir if stage == 2 else outdir / "etap1"
    zdir.mkdir(parents=True, exist_ok=True)
    cache = OUT / "_a3"
    jpgs = [board_a3(stage, n, cache, notes) for n in ns]
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for title, p in comps:
        w.append(str(p), outline_item=title, import_outline=(p.parent == outdir))
    if jpgs:
        bp = cache / f"_plansze_etap{stage}.pdf"
        images_pdf(jpgs, bp)
        start = len(w.pages)
        w.append(str(bp), import_outline=False)
        parent = w.add_outline_item(title="Plansze pomniejszone do A3", page_number=start)
        for k, n in enumerate(ns):
            w.add_outline_item(title=f"Plansza {n}", page_number=start + k, parent=parent)
    neutral_writer(w, f"Część opisowa – {st['label']}")
    out = zdir / "CZESC_OPISOWA.pdf"
    tmp = out.with_suffix(".tmp.pdf")
    with open(tmp, "wb") as fh:
        w.write(fh)
    tmp.replace(out)
    r = PdfReader(str(out))
    k = 72 / 25.4
    sizes = [(round(float(pg.mediabox.width) / k), round(float(pg.mediabox.height) / k)) for pg in r.pages]
    md = check_metadata(out)
    mb = out.stat().st_size / 2 ** 20
    log(f"── ZESZYT {st['label']}: {out.relative_to(ROOT)} – {len(r.pages)} stron, {mb:.1f} MB "
        f"({'≤ 100 MB OK' if mb <= 100 else 'PRZEKRACZA 100 MB (R-131/S-01)'})")
    pos = 0
    for title, p in comps:
        n = len(PdfReader(str(p)).pages)
        log(f"   s. {pos + 1}–{pos + n}: {title} [{p.relative_to(ROOT)}] {sorted(set(sizes[pos:pos + n]))} mm")
        pos += n
    if jpgs:
        log(f"   s. {pos + 1}–{pos + len(jpgs)}: plansze A3 {ns} {sorted(set(sizes[pos:]))} mm")
    for nn in notes:
        log(f"   {nn}")
    for m in missing:
        log(f"   ✖ BRAK (wersja robocza --allow-missing): {m}")
    log(f"   metadane: {md['metadane']} · XMP: {'jest' if md['xmp'] else 'brak'} · {'OK' if md['ok'] else 'DO POPRAWY'}")
    if mb > 100:
        raise OpisError("zeszyt > 100 MB")
    return 3 if missing else 0


# ------------------------------------------------------------------------------------------------ --check / --test
def check_only(paths):
    models, mmeta = load_models()
    code = 0
    for p in paths:
        p = Path(p).resolve()
        try:
            doc = parse_document(p, models)
        except PlaceholderError as e:
            log(f"✖ {p}: {len(e.errors)} błąd(y):")
            for x in e.errors:
                log("   " + x)
            code = 1
            continue
        log(f"✔ {doc['fname']}: {len(doc['used'])} placeholderów, LEDGER {len(doc['ledger'])} poz., "
            f"liczby dosłowne spoza LEDGER: {len(doc['literal'])}")
        for x in doc["literal"][:40]:
            log(f"   ? w.{x['wiersz']}: {x['liczba']}  ← „{x['kontekst']}”")
        for w in doc["ctx"].warnings:
            log(f"   UWAGA: {w}")
    return code


def run_tests(png=True):
    ok, fail = [], []

    def t(name, cond, info=""):
        (ok if cond else fail).append(name)
        log(f"  [{'PASS' if cond else 'FAIL'}] {name}{(' – ' + info) if info else ''}")

    log("== 1. formatowanie liczb (zapis polski)")
    cases = [((14392.7, 1), "14 392,7"), ((1185, 0), "1185"), ((8871.47, 2), "8871,47"), ((-7.0, 2), "−7,00"),
             ((2.675, 2), "2,68"), ((-0.004, 2), "0,00"), ((12345678.9, 0), "12 345 679"), ((37.62, 1), "37,6"),
             ((0.215, None), "0,215"), ((81408, 0), "81 408"), ((10000, 0), "10 000"), ((9999.5, 0), "10 000")]
    for (v, d), exp in cases:
        got = fmt_number(v, d)
        t(f"fmt({v!r}, {d}) = {exp!r}", got == exp, f"otrzymano {got!r}")
    log("== 2. ścieżki modelu (porównanie z bezpośrednim odczytem JSON)")
    models, _ = load_models()
    K, B = models["K"], models["B"]
    w = next(b for b in K["bryly"] if b["id"] == "W")
    s_kond = next(x for x in B["kondygnacje"] if x["id"] == "S")
    probes = [("K", "bryly[id=W].dach.attyka.nad_najnizszym_terenem_A", "2", w["dach"]["attyka"]["nad_najnizszym_terenem_A"]),
              ("K", "bilans.PC_nadziemna_m2", "1", K["bilans"]["PC_nadziemna_m2"]),
              ("K", "teren.wieza_2m.0", "2", K["teren"]["wieza_2m"][0]),
              ("K", "podziemie.-1.miejsca", "0", K["podziemie"]["-1"]["miejsca"]),
              ("K", "kondygnacje[kondygnacja=S].posadzka_npm", "2",
               next(x for x in K["kondygnacje"] if x["kondygnacja"] == "S")["posadzka_npm"]),
              ("B", "kondygnacje[id=-2].rzedna", "2", next(x for x in B["kondygnacje"] if x["id"] == "-2")["rzedna"]),
              ("B", f"kondygnacje[id=S].pomieszczenia[numer={s_kond['pomieszczenia'][0]['numer']}].powierzchnia", "2",
               s_kond["pomieszczenia"][0]["powierzchnia"]),
              ("K", "meta.wersja", "raw", K["meta"]["wersja"])]
    for src, path, fmt, raw in probes:
        got = format_value(resolve_path(models[src], path), fmt)
        exp = raw if fmt == "raw" else fmt_number(raw, int(fmt))
        t(f"{{{{{src}:{path}|{fmt}}}}} → {got!r}", got == exp)
    for path, frag in [("bryly[id=X].pow_rzutu_m2", "brak elementu [id=X]"), ("bilans.nie_ma", "brak klucza „nie_ma”"),
                       ("bryly.pow", "jest listą"), ("meta.nazwa", None), ("teren.wieza_2m.9", "poza listą")]:
        try:
            resolve_path(K, path)
            t(f"ścieżka {path} rozwiązana", frag is None)
        except ResolveError as e:
            t(f"ścieżka {path} → błąd „{frag}”", frag is not None and frag in str(e), str(e)[:90])
    for v, fmt, frag in [("tekst", "2", "nie jest liczbą"), (12.5, "x", "nieznany format"), (None, "1", "null"),
                         ({"a": 1}, "raw", "nie jest skalarem")]:
        try:
            format_value(v, fmt)
            t(f"format_value({v!r},{fmt}) błąd", False)
        except ResolveError as e:
            t(f"format_value({v!r},{fmt}) → „{frag}”", frag in str(e))
    tout = OUT / "_test"
    shutil.rmtree(tout, ignore_errors=True)
    log("== 3. błędne ścieżki w pliku → twardy błąd z plik:wiersz")
    bad = TEST_DIR / "blad_sciezki.md"
    try:
        render_stage(2, bad, tout, png=False, quiet=True)
        t("blad_sciezki.md odrzucony", False)
    except PlaceholderError as e:
        for x in e.errors:
            log("     " + x)
        lines = bad.read_text(encoding="utf-8").split("\n")
        exp_lines = [k for k, l in enumerate(lines, 1) if "{{" in l and "OK" not in l]
        got_lines = sorted({int(re.search(r":(\d+):", x).group(1)) for x in e.errors})
        t("wszystkie błędne placeholdery zgłoszone z numerem wiersza", got_lines == exp_lines, f"{got_lines} vs {exp_lines}")
        t("nie powstał HTML/PDF z pustymi wartościami",
          not (tout / "opis_etap2_A3.html").exists() and not (tout / "opis_etap2_A3.pdf").exists())
    log("== 4. Etap II – fixture (A3 poziomo, 3 łamy)")
    r2 = render_stage(2, TEST_DIR / "etap2_opis.md", tout, png=png)
    p2 = r2["czesci"]["tekst"]
    t("strony ≤ 5", p2["strony"] <= 5, f"{p2['strony']} str.")
    t("format A3 poziomo na każdej stronie (±0,6 mm)", all(abs(f[0] - 420) <= 0.6 and abs(f[1] - 297) <= 0.6
                                                           for f in p2["format_mm"]), str(p2["format_mm"][:1]))
    t("najmniejsza czcionka w PDF ≥ 11 pt", (p2["min_pt"] or 0) >= MIN_PT - 0.005, f"{p2['min_pt']} pt")
    t("najmniejsza czcionka w CSS ≥ 11 pt", p2["css_min_pt"] >= MIN_PT, f"{p2['css_min_pt']} pt")
    t("tylko kroje Inter / Inter Display", not p2["zastepcze"], ", ".join(sorted(p2["czcionki"])))
    t("brak przepełnień łamów", not p2["przepelnienia"], str(p2["przepelnienia"][:2]))
    t("metadane PDF neutralne, bez XMP", r2["metadane"]["ok"], str(r2["metadane"]["metadane"]))
    html2 = (tout / "opis_etap2_A3.html").read_text(encoding="utf-8")
    t("LEDGER i komentarze usunięte z wydruku", "LEDGER" not in html2 and "<!--" not in html2)
    t("wartości z modelu w HTML (zapis polski)", fmt_number(K["bilans"]["PC_nadziemna_m2"], 1) in html2
      and fmt_number(w["dach"]["attyka"]["nad_najnizszym_terenem_A"], 2) in html2)
    t("dzielenie wyrazów (miękkie łączniki pl)", SHY in html2)
    t('lang="pl" + hyphens:auto', 'lang="pl"' in html2 and "hyphens: auto" in html2)
    log("== 5. Etap II – za długi tekst → limit 5 stron")
    src = (TEST_DIR / "etap2_opis.md").read_text(encoding="utf-8")
    body = COMMENT_RE.sub("", src)
    long_md = tout / "etap2_za_dlugi.md"
    long_md.write_text("\n\n".join([body] * 8) + "\n", encoding="utf-8")
    r5 = render_stage(2, long_md, tout / "za_dlugi", png=False, quiet=True)
    t("przekroczenie wykryte (kod 2)", r5["kod"] == 2 and r5["czesci"]["tekst"]["strony"] > 5,
      f"{r5['czesci']['tekst']['strony']} str.")
    log("== 6. Etap I – fixture (A4 pionowo + załącznik po <!-- ANNEX -->)")
    r1 = render_stage(1, TEST_DIR / "etap1_opis.md", tout, png=png)
    p1 = r1["czesci"]["tekst"]
    t("strony tekstu ≤ 5", p1["strony"] <= 5, f"{p1['strony']} str.")
    t("załącznik liczony osobno", "zalacznik" in r1["czesci"], f"{r1['czesci'].get('zalacznik', {}).get('strony')} str.")
    t("format A4 pionowo (±0,6 mm)", all(abs(f[0] - 210) <= 0.6 and abs(f[1] - 297) <= 0.6
                                         for part in r1["czesci"].values() for f in part["format_mm"]))
    t("najmniejsza czcionka w PDF ≥ 11 pt (tekst + zał.)",
      all((p["min_pt"] or 0) >= MIN_PT - 0.005 for p in r1["czesci"].values()))
    t("brak przepełnień", not any(p["przepelnienia"] for p in r1["czesci"].values()))
    from pypdf import PdfReader
    n_all = len(PdfReader(str(tout / "opis_etap1_A4.pdf")).pages)
    t("PDF Etapu I = tekst + załącznik", n_all == p1["strony"] + r1["czesci"]["zalacznik"]["strony"], f"{n_all} str.")
    log("== 7. zeszyt Etapu II (tekst fixture'u + F.15.A/B/C + F.14.B + plansze A3)")
    try:
        zc = build_zeszyt(2, False, False, TEST_DIR / "etap2_opis.md", tout)
        zp = tout / "CZESC_OPISOWA.pdf"
        rz = PdfReader(str(zp))
        exp_n = p2["strony"] + sum(len(PdfReader(str(ROOT / "build" / "tabele" / f"{c}.pdf")).pages)
                                   for c in ("F.15.A", "F.15.B", "F.15.C", "F.14.B")) + len(board_numbers(2))
        t("zeszyt złożony, liczba stron = tekst + tabele + plansze", zc == 0 and len(rz.pages) == exp_n,
          f"{len(rz.pages)} / oczekiwano {exp_n}")
        k = 72 / 25.4
        t("wszystkie strony zeszytu A3 poziomo (±1 mm)", all(abs(float(pg.mediabox.width) / k - 420) <= 1 and
                                                         abs(float(pg.mediabox.height) / k - 297) <= 1 for pg in rz.pages))
        md = check_metadata(zp)
        t("metadane zeszytu neutralne (tylko /Title), bez XMP", md["ok"], str(md["metadane"]))
        t("zakładki PDF (tekst, tabele, plansze)", len(rz.outline) >= 6, f"{len(rz.outline)} pozycji najwyższego poziomu")
        t("zeszyt ≤ 100 MB (R-131)", zp.stat().st_size <= 100 * 2 ** 20, f"{zp.stat().st_size / 2 ** 20:.1f} MB")
    except OpisError as e:
        t("zeszyt Etapu II złożony", False, str(e))
    log("== 8. zeszyt Etapu I bez F.14.A → odmowa (kod 3); z --allow-missing → wersja robocza")
    f14a = ROOT / "build" / "tabele" / "F.14.A.pdf"
    if f14a.exists():
        t("F.14.A istnieje – test odmowy pominięty", True)
    else:
        try:
            build_zeszyt(1, False, False, TEST_DIR / "etap1_opis.md", tout)
            t("odmowa przy braku F.14.A", False)
        except OpisError as e:
            t("odmowa przy braku F.14.A (kod 3)", e.code == 3, str(e))
        zc1 = build_zeszyt(1, True, False, TEST_DIR / "etap1_opis.md", tout)
        t("wersja robocza z --allow-missing (kod 3, plik powstał)", zc1 == 3 and (tout / "etap1" / "CZESC_OPISOWA.pdf").exists())
    log(f"== WYNIK: {len(ok)} PASS, {len(fail)} FAIL")
    for f in fail:
        log(f"   FAIL: {f}")
    return 0 if not fail else 4


# ------------------------------------------------------------------------------------------------ main
def _ensure_venv():
    py = VENV / "bin" / "python"
    if os.environ.get("OPIS_NO_VENV") or not py.exists():
        return
    if Path(sys.prefix).resolve() == VENV.resolve():
        return
    os.execv(str(py), [str(py), "-I", str(Path(__file__).resolve()), *sys.argv[1:]])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Renderer części opisowej (Etap II: 5×A3, Etap I: 5×A4 + zał.)")
    ap.add_argument("--etap", choices=["1", "2", "oba"], default=None)
    ap.add_argument("--src", type=Path, help="plik .md zamiast docs/95_opis/etapN_opis.md (z --etap 1|2)")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--bez-podgladu", action="store_true", help="bez PNG")
    ap.add_argument("--check", nargs="+", metavar="PLIK.md", help="tylko placeholdery + LEDGER")
    ap.add_argument("--zeszyt", action="store_true", help="build/opis/CZESC_OPISOWA.pdf (Etap II)")
    ap.add_argument("--zeszyt-etap1", action="store_true", help="build/opis/etap1/CZESC_OPISOWA.pdf (Etap I)")
    ap.add_argument("--allow-missing", action="store_true", help="zeszyt roboczy mimo braków (kod 3)")
    ap.add_argument("--test", action="store_true", help="fixture'y docs/95_opis/_test + testy negatywne")
    a = ap.parse_args(argv)
    png = not a.bez_podgladu
    try:
        if a.check:
            return check_only(a.check)
        if a.test:
            return run_tests(png)
        if a.zeszyt or a.zeszyt_etap1:
            code = 0
            if a.src and a.zeszyt and a.zeszyt_etap1:
                ap.error("--src z jednym rodzajem zeszytu naraz")
            if a.zeszyt:
                code = max(code, build_zeszyt(2, a.allow_missing, png, a.src, a.out.resolve()))
            if a.zeszyt_etap1:
                code = max(code, build_zeszyt(1, a.allow_missing, png, a.src, a.out.resolve()))
            return code
        if a.src and a.etap not in ("1", "2"):
            ap.error("--src wymaga --etap 1 albo --etap 2")
        stages = [2, 1] if a.etap in (None, "oba") else [int(a.etap)]
        code, done = 0, 0
        for s in stages:
            src = a.src.resolve() if a.src else SRC_DIR / STAGES[s]["src"]
            if not src.exists():
                log(f"(pomijam {STAGES[s]['label']}: brak {src.relative_to(ROOT) if src.is_relative_to(ROOT) else src})")
                continue
            r = render_stage(s, src, a.out.resolve(), png=png)
            code, done = max(code, r["kod"]), done + 1
        if not done:
            log("Brak plików wejściowych docs/95_opis/etap{1,2}_opis.md – tryb testowy: tools/opis.py --test")
            return 1
        return code
    except PlaceholderError as e:
        log(f"✖ BŁĄD PLACEHOLDERÓW ({len(e.errors)}):")
        for x in e.errors:
            log("   " + x)
        return 1
    except OpisError as e:
        log(f"✖ {e}")
        return e.code


if __name__ == "__main__":
    _ensure_venv()
    sys.exit(main())
