"""Redakcja tekstów pobieranych z modelu i rejestru wymagań do części opisowej tomu I (PZT, PAB, ZL).

Model (``model/*.yaml``) i rejestr (``wymagania.yaml``) zawierają adnotacje robocze zespołu projektowego — odsyłacze
do audytów (A1, J1, K-2), rund weryfikacji, briefu, raportów badawczych (R1…R8) i sprzeczności (S-n). W tekście
urzędowym nie są one podstawą prawną ani treścią projektu, więc usuwa się je przy każdym generowaniu (model
pozostaje bez zmian). Zachowuje się identyfikatory rejestru wymagań (W-xxx, D-xx) oraz znaczniki E.1.

``PODSTAWY`` — podstawy prawne sprawdzone w tekście urzędowym (API ELI Sejmu), które zastępują w opisie brzmienie
pola ``zrodlo`` rejestru, gdy to jest nieścisłe (lista poniżej, z uzasadnieniem).
"""
from __future__ import annotations

import re

from lamela.dokumenty.znaczniki import INT, ZAL

# (sekcja, klucz) → podstawa sprawdzona w tekście urzędowym
PODSTAWY = {
    # WT (t.j. Dz.U. 2022 poz. 1225): § 329 ust. 1 — wzór EP = EP_H+W + ΔEP_C + ΔEP_L; ust. 2 — tabela cząstkowych
    # wartości EP_H+W (lp. 1 lit. a: jednorodzinny, od 31.12.2020 r.); § 328 ust. 1 pkt 1 — wymaganie EP ≤ EP_max
    ("energia", "EP_max"): "WT § 328 ust. 1 pkt 1, § 329 ust. 1–2 (EP_H+W, tabela lp. 1 lit. a — budynek mieszkalny "
                           "jednorodzinny, od 31.12.2020 r.) [W-240]",
    # WT § 183 ust. 2: PWP w strefach pożarowych o kubaturze > 1000 m³; ust. 3: lokalizacja i oznakowanie
    ("elektryka", "PWP_kubatura_strefy_prog"): "WT § 183 ust. 2 [W-190]",
    # rozp. Dz.U. 2012 poz. 463 § 4 ust. 3 pkt 2 lit. a — druga kategoria geotechniczna (fundamenty bezpośrednie)
    ("geotechnika", "kategoria_geotechniczna"): "rozp. Dz.U. 2012 poz. 463 § 4 ust. 3 pkt 2 lit. a [W-280]",
    # WT § 316 ust. 2 — odprowadzenie wód od budynku; wartość 2 % jest założeniem projektowym (rejestr W-019 [ZAŁ])
    ("usytuowanie", "spadek_terenu_od_budynku_min"): f"WT § 316 ust. 2 (spływ wód od budynku); 2 % — założenie "
                                                     f"projektowe {ZAL} [W-019]",
}

# pojedyncze człony adnotacji roboczych (po podziale treści nawiasu na „, ” i „; ”)
_ROBOCZE = re.compile(
    r"^(?:audyt\w*\s+[AJ]\d.*|[AJ]\d(?:/[AJ]\d)*(?:\s+[A-Z]-?\d+)?|K-\d+|B\d+|S-\d+|D-\d+\s*\(roboc.*|brief.*|"
    r"R\d(?:[ -][\w.]+)*|R\d-\d+|runda.*|BRAKI.*|weryfikacj.*|powiększon.*|sprzeczno\w* S-\d+|"
    r"TWARDE ZAŁOŻENIA.*|przeszczep.*|poprawion\w* po audycie.*)$", re.I)
_NAWIAS = re.compile(r"\(([^()]*)\)")


def _czysc_nawias(m: re.Match) -> str:
    czlony = [c.strip() for c in re.split(r";\s*|,\s+", m.group(1))]
    zostaw = [c for c in czlony if c and not _ROBOCZE.match(c)]
    if len(zostaw) == len([c for c in czlony if c]):
        return m.group(0)
    return f"({', '.join(zostaw)})" if zostaw else ""


def czysc(txt) -> str:
    """Usuwa adnotacje robocze z opisu pochodzącego z modelu lub rejestru; zapis liczb — przecinek dziesiętny."""
    t = str(txt if txt is not None else "")
    t = _NAWIAS.sub(_czysc_nawias, t)
    t = re.sub(r"\s*[—–-]\s*(?:sprzeczno\w* S-\d+|runda \d+)", "", t)
    t = re.sub(r"\s*[—–-]\s*(?:R\d [\d.]+|R\d-\d+|audyt\w* [AJ]\d[^;,)]*)", "", t)
    t = re.sub(r"(?:;\s*|,\s*)?\b(?:R\d [\d.]+|R\d-\d+|R\d-R\d|audyt\w* [AJ]\d|K-\d+)\b", "", t)
    t = re.sub(r"\bTWARDE ZAŁOŻENIA\b", f"założenie projektowe {ZAL}", t)
    t = re.sub(r"\bbrief\s*§\s*\d+(?:\s*pkt\s*\d+)?(?:\.\d+)?", "", t)
    t = re.sub(r"§(?=\d)", "§ ", t)
    t = re.sub(r"\((?:\s*[;,]?\s*)\)", "", t)
    t = re.sub(r"\[\s*[;,]?\s*\]", "", t)
    t = re.sub(r"\s+([,;.)])", r"\1", t)
    t = re.sub(r"\(\s*[;,]\s*", "(", t)
    t = re.sub(r"^[;,]\s*|\s*[;,]\s*$", "", t.strip())
    t = re.sub(r"\s{2,}", " ", t).strip()
    return _scal_id(t)


def _scal_id(t: str) -> str:
    """„[W-144] [W-144, W-145]” → „[W-144, W-145]” (kolejne nawiasy z identyfikatorami rejestru)."""
    def scal(m):
        ids = []
        for g in re.findall(r"\[([^\]]*)\]", m.group(0)):
            ids += [x.strip() for x in g.split(",") if x.strip() and x.strip() not in ids]
        return "[" + ", ".join(ids) + "]"
    return re.sub(r"\[(?:W|D)-\d+[^\]]*\](?:\s*\[(?:W|D)-\d+[^\]]*\])+", scal, t)


def liczby_pl(txt) -> str:
    """Zapis liczb w oznaczeniach wyrobów wg konwencji polskiej: „DN150 i=0.02” → „DN150, i = 0,02”; „Q3=6.3” → „Q3 = 6,3”."""
    t = re.sub(r"(\d)\.(\d)", r"\1,\2", str(txt))
    t = re.sub(r"\s*=\s*", " = ", t)
    return re.sub(r"(\S) (i = )", r"\1, \2", t)


def podstawa(zr: str, sekcja: str | None = None, klucz: str | None = None) -> str:
    """Podstawa wartości normatywnej do tekstu urzędowego: sprawdzona (``PODSTAWY``) albo oczyszczona z rejestru.
    Pozostałość pusta (np. sam odsyłacz do raportu badawczego) → założenie projektowe [ZAŁ]."""
    if (sekcja, klucz) in PODSTAWY:
        return PODSTAWY[(sekcja, klucz)]
    t = czysc(zr)
    if not re.sub(r"\[W-\d+[^\]]*\]|\[ZAŁ\]|[\s;,]", "", t):
        t = (f"założenie projektowe {ZAL} " + t).strip()
    return t


def odmiana(n: int, jeden: str, kilka: str, wiele: str) -> str:
    """Forma liczebnikowa: 1 pole, 2–4 pola, 5 pól (12–14 — „wiele”)."""
    if n == 1:
        return jeden
    return kilka if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else wiele


LEGENDA = (f"**Oznaczenia:** [DO UZUPEŁNIENIA: …] — dane do uzupełnienia przed złożeniem wniosku (dane osobowe, "
           f"numery uprawnień, decyzje i uzgodnienia); [DANE PRZYKŁADOWE – FIKCYJNE] — dane przykładowe (działka, "
           f"MPZP, uzbrojenie, podłoże, wyroby); [DOKUMENT ZEWNĘTRZNY – …] — miejsce dokumentu wydanego przez organ; "
           f"{ZAL} — założenie projektowe; [NZW] — wartość lub rozwiązanie niezweryfikowane, do potwierdzenia na etapie "
           f"projektu technicznego lub planu BIOZ; {INT} — przyjęta interpretacja przepisu.")
