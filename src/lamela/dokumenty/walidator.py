"""Walidator kompletności tomu wg listy kontrolnej (rejestr wymagań, sekcja C; ``listy_kontrolne.yaml``).

``sprawdz_tom(tom, lista)`` czyta **gotowy plik PDF** (także spoza systemu): zakładki, tekst stron, formaty stron,
obrazy rastrowe, metadane, rozmiar i nazwę pliku. Elementy tomu (PZT, PAB, ZL, PT) rozpoznaje po zakładkach
najwyższego poziomu „KOD — tytuł” (``Tom``); plik bez takich zakładek traktuje jako jeden element listy.

Statusy pozycji: ``OK`` · ``BRAK`` · ``DO UZUPEŁNIENIA`` (jest, ale z polem ``[DO UZUPEŁNIENIA]`` na stronie
tytułowej) · ``N/D`` (nie dotyczy, z podstawą) · ``OSTRZEŻENIE`` (pozycja nieobowiązkowa nieznaleziona).
Status tomu: ``NIEKOMPLETNY`` (brak pozycji obowiązkowej) → ``PRZYKŁAD – NIE DO ZŁOŻENIA`` (są znaczniki
``[DO UZUPEŁNIENIA]`` / ``[DOKUMENT ZEWNĘTRZNY]`` — reguła AUD-RYS, rejestr E.1) → ``KOMPLETNY FORMALNIE``.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field, asdict
from pathlib import Path

import pymupdf
import yaml

from .formaty import PT2MM, wykryj_format, odmiana
from .nazwy import sprawdz_nazwe
from .znaczniki import policz_znaczniki, blokuje_zlozenie, STATUS_PRZYKLAD

PLIK_LIST = Path(__file__).with_name("listy_kontrolne.yaml")
LIMIT_MB = 150.0


def _wczytaj_listy() -> dict:
    with open(PLIK_LIST, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    out = {}
    for k, v in raw.items():
        if not isinstance(v, dict) or "pozycje" not in v:
            continue
        poz = list(raw.get(v["wspolne"], [])) + list(v["pozycje"]) if v.get("wspolne") else list(v["pozycje"])
        out[k] = dict(v, pozycje=poz, klucz=k)
    return out


LISTY_KONTROLNE = _wczytaj_listy()


@dataclass
class Pozycja:
    id: str
    element: str
    opis: str
    podstawa: str
    status: str
    obowiazkowa: bool = True
    szczegoly: str = ""


@dataclass
class RaportKompletnosci:
    plik: str
    lista: str
    status: str
    pozycje: list = field(default_factory=list)
    znaczniki: dict = field(default_factory=dict)
    elementy: dict = field(default_factory=dict)
    rozmiar_mb: float = 0.0
    strony: int = 0

    @property
    def braki(self) -> list[Pozycja]:
        return [p for p in self.pozycje if p.status == "BRAK" and p.obowiazkowa]

    @property
    def do_uzupelnienia(self) -> list[Pozycja]:
        return [p for p in self.pozycje if p.status == "DO UZUPEŁNIENIA"]

    def podsumowanie(self) -> dict:
        c = Counter(p.status for p in self.pozycje)
        return {"status": self.status, **{k: c.get(k, 0) for k in ("OK", "BRAK", "DO UZUPEŁNIENIA", "N/D", "OSTRZEŻENIE")},
                "znaczniki_do_uzupelnienia": self.znaczniki.get("DO UZUPEŁNIENIA", 0),
                "znaczniki_dokument_zewnetrzny": self.znaczniki.get("DOKUMENT ZEWNĘTRZNY", 0),
                "znaczniki_dane_przykladowe": self.znaczniki.get("DANE PRZYKŁADOWE", 0)}

    def json(self) -> dict:
        d = asdict(self)
        d["znaczniki"] = {k: (dict(v) if isinstance(v, Counter) else v) for k, v in self.znaczniki.items()}
        d["podsumowanie"] = self.podsumowanie()
        return d

    def zapisz_json(self, sciezka):
        Path(sciezka).write_text(json.dumps(self.json(), ensure_ascii=False, indent=2), encoding="utf-8")

    def tekst(self) -> str:
        s = self.podsumowanie()
        L = [f"RAPORT KOMPLETNOŚCI — {self.plik}", f"Lista kontrolna: {self.lista}",
             f"Status: {self.status}",
             f"Pozycje: OK {s['OK']} · BRAK {s['BRAK']} · DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']} · N/D {s['N/D']} · "
             f"OSTRZEŻENIE {s['OSTRZEŻENIE']}",
             f"Znaczniki: [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}, [DOKUMENT ZEWNĘTRZNY] "
             f"×{s['znaczniki_dokument_zewnetrzny']}, [DANE PRZYKŁADOWE] ×{s['znaczniki_dane_przykladowe']}",
             f"Plik: {self.strony} stron, {self.rozmiar_mb:.2f} MB", ""]
        for el, info in self.elementy.items():
            L.append(f"  element {el}: strony {info['od']}–{info['do']} (opis {info['strony_opisu']}, "
                     f"arkusze {info['arkusze']})")
        L.append("")
        szer = max((len(p.id) for p in self.pozycje), default=6)
        for p in self.pozycje:
            znak = {"OK": "✓", "BRAK": "✗", "DO UZUPEŁNIENIA": "…", "N/D": "–", "OSTRZEŻENIE": "!"}.get(p.status, "?")
            L.append(f"{znak} {p.id:<{szer}} [{p.element:>3}] {p.status:<16} {p.opis} ({p.podstawa})"
                     + (f" — {p.szczegoly}" if p.szczegoly else ""))
        lista = self.znaczniki.get("lista") or {}
        if lista:
            L += ["", "Pola do uzupełnienia i dokumenty zewnętrzne (wystąpienia):"]
            for k, n in sorted(lista.items(), key=lambda x: (-x[1], x[0])):
                if "DANE PRZYKŁADOWE" in k or k in ("[ZAŁ]", "[NZW]", "[INT]", "[PROG]"):
                    continue
                L.append(f"  {n:>3} × {k}")
        return "\n".join(L)


# ================================================================================================= analiza PDF
_RE_EL = re.compile(r"^(PZT|PAB|ZL|PT(?:[ -]\d+)?(?:[ -][A-Z]{2})?)\s+—\s+")


def _norm(t: str) -> str:
    t = t.replace("­", "")
    t = re.sub(r"-\n(?=[a-ząćęłńóśźż])", "", t)
    return re.sub(r"\s+", " ", t)


def _czy_a4_pion(page) -> bool:
    return abs(page.rect.width - 595.3) < 3 and abs(page.rect.height - 841.9) < 3


def _analiza(doc: pymupdf.Document, lista: dict) -> dict:
    toc = doc.get_toc(simple=True)
    n = doc.page_count
    teksty = [_norm(p.get_text()) for p in doc]
    a4 = [_czy_a4_pion(p) for p in doc]
    # elementy z zakładek 1. poziomu „KOD — tytuł”
    starty = []
    for lvl, t, s in toc:
        if lvl == 1:
            m = _RE_EL.match(t)
            if m:
                kod = m.group(1).split()[0].split("-")[0]
                starty.append((kod, s))
    elementy = {}
    if starty:
        for i, (kod, s) in enumerate(starty):
            e = (starty[i + 1][1] - 1) if i + 1 < len(starty) else n
            elementy[kod] = dict(od=s, do=e)
    else:
        kod = (lista.get("elementy") or ["*"])[0]
        elementy[kod] = dict(od=1, do=n)
    for kod, r in elementy.items():
        rng = range(r["od"] - 1, r["do"])
        r["zakladki"] = [t for lvl, t, s in toc if r["od"] <= s <= r["do"] and not (lvl == 1 and _RE_EL.match(t))]
        r["rysunki"] = [t for lvl, t, s in toc if r["od"] <= s <= r["do"] and 0 <= s - 1 < n and not a4[s - 1]]
        r["zastepcze"] = {t for lvl, t, s in toc if r["od"] <= s <= r["do"] and 0 <= s - 1 < n and not a4[s - 1]
                          and "ARKUSZ ZASTĘPCZY" in teksty[s - 1]}
        r["tytulowa"] = teksty[r["od"] - 1] if r["od"] - 1 < n else ""
        r["tekst"] = " ".join(teksty[i] for i in rng if a4[i])
        r["strony_opisu"] = sum(1 for i in rng if a4[i])
        r["arkusze"] = sum(1 for i in rng if not a4[i])
        r["strony_a4"] = [i for i in rng if a4[i]]
    return dict(toc=toc, teksty=teksty, a4=a4, elementy=elementy)


def _szukaj(wzorce, gdzie) -> list[str]:
    tr = []
    for w in wzorce:
        rx = re.compile(w.replace(" ", r"\s+"), re.I)
        if isinstance(gdzie, str):
            if rx.search(gdzie):
                tr.append(w)
        else:
            if any(rx.search(g) for g in gdzie):
                tr.append(w)
    return tr


def _spec(nazwa, doc, sciezka, an, lista, el_info) -> tuple[str, str]:
    if nazwa == "nazwa_pliku":
        ok, opis = sprawdz_nazwe(Path(sciezka).name, lista.get("nazwa_pliku"))
        if ok and lista.get("symbol") and f"_{lista['symbol']}_" not in Path(sciezka).name:
            return "BRAK", f"symbol specjalności w nazwie ≠ {lista['symbol']}"
        return ("OK" if ok else "BRAK"), opis
    if nazwa == "rozmiar":
        mb = Path(sciezka).stat().st_size / 1048576
        return ("OK" if mb <= LIMIT_MB else "BRAK"), f"{mb:.2f} MB (limit {LIMIT_MB:.0f} MB)"
    if nazwa == "metadane":
        m = doc.metadata or {}
        brak = [k for k in ("title", "subject") if not (m.get(k) or "").strip()]
        return ("OK" if not brak else "BRAK"), (f"Title: „{m.get('title', '')}”" if not brak else f"brak: {brak}")
    if nazwa == "wektor":
        rastrowe = []
        for i, p in enumerate(doc):
            if an["a4"][i]:
                continue
            pole = p.rect.width * p.rect.height
            s = sum(abs(pymupdf.Rect(im["bbox"]).get_area()) for im in p.get_image_info())
            if s > 0.35 * pole:
                rastrowe.append(i + 1)
        n_ark = sum(1 for x in an["a4"] if not x)
        if rastrowe:
            return "BRAK", f"arkusze z dominującym rastrem na stronach {rastrowe} (dopuszczalny tylko podkład mapy)"
        return "OK", (f"{n_ark} {odmiana(n_ark, 'arkusz wektorowy', 'arkusze wektorowe', 'arkuszy wektorowych')}"
                      if n_ark else "brak arkuszy w pliku")
    if nazwa == "oprawa_pt":
        pt = [k for k in an["elementy"] if k.startswith("PT")]
        return ("BRAK" if pt else "OK"), ("PT we wspólnej oprawie" if pt else "brak PT w pliku")
    if nazwa == "tom_pt":
        inne = [k for k in an["elementy"] if not k.startswith("PT") and k != "*"]
        return ("BRAK" if inne else "OK"), (f"inne elementy w pliku: {inne}" if inne else "plik zawiera tylko tom PT")
    if nazwa == "numeracja":
        if el_info is None:
            return "BRAK", "element nieznaleziony"
        strony = el_info["strony_a4"][1:]          # bez strony tytułowej
        bez = [i + 1 for i in strony if not re.search(r"strona\s+\d+\s+z\s+\d+", an["teksty"][i])]
        return ("OK" if not bez else "BRAK"), (f"{len(strony)} stron numerowanych" if not bez
                                               else f"brak numeru na stronach pliku {bez[:8]}")
    return "BRAK", f"nieznana kontrola {nazwa}"


def sprawdz_tom(tom, lista_kontrolna: dict | str | None = None) -> RaportKompletnosci:
    """Sprawdza kompletność tomu. ``tom`` — ścieżka PDF, ``WynikTomu``, ``WynikDokumentu`` (z zapisaną ścieżką).
    ``lista_kontrolna`` — słownik z ``LISTY_KONTROLNE`` lub jego klucz ('TOM_I', 'PT_AR', …); ``None`` — dobór
    po nazwie pliku."""
    if hasattr(tom, "wynik") and getattr(tom, "wynik", None) is not None:      # obiekt Tom po zloz()
        if lista_kontrolna is None and getattr(tom, "rodzaj", None) == "PT" and getattr(tom, "symbol", None):
            lista_kontrolna = f"PT_{tom.symbol}"
        tom = tom.wynik
    elif hasattr(tom, "zloz"):
        raise ValueError("Tom nie został złożony — wywołaj najpierw tom.zloz(katalog)")
    sciezka = Path(getattr(tom, "sciezka", None) or tom)
    if isinstance(lista_kontrolna, str):
        lista = LISTY_KONTROLNE[lista_kontrolna]
    elif lista_kontrolna is None:
        m = re.match(r"^PT_\d+_([A-Z]{2})_", sciezka.name)
        lista = LISTY_KONTROLNE.get(f"PT_{m.group(1)}") if m else LISTY_KONTROLNE["TOM_I"]
        if lista is None:
            raise ValueError(f"Brak listy kontrolnej dla {sciezka.name}")
    else:
        lista = lista_kontrolna
    doc = pymupdf.open(str(sciezka))
    try:
        an = _analiza(doc, lista)
        pozycje = []
        for poz in lista["pozycje"]:
            el = poz.get("el", "*")
            ob = bool(poz.get("obowiazkowa", True))
            base = dict(id=poz["id"], element=el, opis=poz["opis"], podstawa=poz.get("podstawa", ""), obowiazkowa=ob)
            if poz.get("nd"):
                pozycje.append(Pozycja(status="N/D", szczegoly=f"nie dotyczy — {poz['nd']}", **base))
                continue
            sz = poz.get("szukaj") or {}
            info = an["elementy"].get(el) if el != "*" else None
            if el != "*" and info is None:
                pozycje.append(Pozycja(status="BRAK" if ob else "OSTRZEŻENIE", szczegoly=f"brak elementu {el} w pliku",
                                       **base))
                continue
            if "spec" in sz:
                st, opis = _spec(sz["spec"], doc, sciezka, an, lista, info)
                if st == "BRAK" and not ob:
                    st = "OSTRZEŻENIE"
                pozycje.append(Pozycja(status=st, szczegoly=opis, **base))
                continue
            if "skala_max" in sz:
                tyt = info["rysunki"] if info else []
                skale = [(t, int(m.group(1))) for t in tyt for m in [re.search(r"\b1\s*:\s*(\d+)", t)] if m]
                zle = [f"{t} (1:{s})" for t, s in skale if s > sz["skala_max"]]
                if not tyt:
                    pozycje.append(Pozycja(status="BRAK" if ob else "OSTRZEŻENIE", szczegoly="brak rysunków", **base))
                else:
                    pozycje.append(Pozycja(status="BRAK" if zle else "OK", szczegoly=(
                        "; ".join(zle) if zle else f"{len(skale)} {odmiana(len(skale), 'rysunek', 'rysunki', 'rysunków')}"
                                                   f" w skali nie mniejszej niż 1:{sz['skala_max']}"), **base))
                continue
            zakres = {"tytulowa": info["tytulowa"] if info else " ".join(an["teksty"][:1]),
                      "zakladki": info["zakladki"] if info else [t for _, t, _ in an["toc"]],
                      "tekst": info["tekst"] if info else " ".join(an["teksty"]),
                      "rysunki": info["rysunki"] if info else []}
            wszystkie = bool(sz.get("wszystkie", False))
            trafione, szczeg = [], []
            zastepczy = False
            wymagane = 0
            for tryb in ("tytulowa", "zakladki", "tekst", "rysunki"):
                if tryb not in sz:
                    continue
                w = sz[tryb]
                wymagane += len(w)
                if tryb == "rysunki" and sz.get("min"):
                    rx = re.compile(w[0].replace(" ", r"\s+"), re.I)
                    ile = sum(1 for t in zakres["rysunki"] if rx.search(t))
                    if ile >= sz["min"]:
                        trafione.append(w[0])
                    szczeg.append(f"rysunków: {ile} (wymagane ≥ {sz['min']})")
                    continue
                tr = _szukaj(w, zakres[tryb])
                trafione += tr
                if tr and tryb == "rysunki":
                    rx = re.compile("|".join(x.replace(" ", r"\s+") for x in tr), re.I)
                    pasujace = [t for t in zakres["rysunki"] if rx.search(t)]
                    szczeg.append("; ".join(pasujace)[:160])
                    if info and pasujace and all(t in info["zastepcze"] for t in pasujace):
                        zastepczy = True
            znaleziono = (len(trafione) >= wymagane) if wszystkie else bool(trafione)
            if znaleziono:
                st = "OK"
                if poz.get("dane_osobowe") and "DO UZUPEŁNIENIA" in zakres["tytulowa"]:
                    st = "DO UZUPEŁNIENIA"
                    szczeg.append("pola [DO UZUPEŁNIENIA] na stronie tytułowej")
                if zastepczy:
                    st = "DO UZUPEŁNIENIA"
                    szczeg.append("tylko arkusz zastępczy — rysunek niedołączony")
            else:
                st = "BRAK" if ob else "OSTRZEŻENIE"
                if wszystkie:
                    brak = [x for tryb in ("tytulowa", "zakladki", "tekst", "rysunki") for x in sz.get(tryb, [])
                            if x not in trafione]
                    szczeg.append("nie znaleziono: " + ", ".join(brak[:4]))
            pozycje.append(Pozycja(status=st, szczegoly="; ".join(s for s in szczeg if s), **base))
        zn = policz_znaczniki(" ".join(an["teksty"]))
        braki = [p for p in pozycje if p.status == "BRAK" and p.obowiazkowa]
        if braki:
            status = "NIEKOMPLETNY"
        elif blokuje_zlozenie(zn) or STATUS_PRZYKLAD in " ".join(an["teksty"][:1]):
            status = STATUS_PRZYKLAD
        else:
            status = "KOMPLETNY FORMALNIE (do weryfikacji merytorycznej projektanta)"
        el_opis = {k: dict(od=v["od"], do=v["do"], strony_opisu=v["strony_opisu"], arkusze=v["arkusze"])
                   for k, v in an["elementy"].items()}
        return RaportKompletnosci(plik=sciezka.name, lista=lista.get("opis", lista.get("klucz", "")), status=status,
                                  pozycje=pozycje, znaczniki=zn, elementy=el_opis,
                                  rozmiar_mb=sciezka.stat().st_size / 1048576, strony=doc.page_count)
    finally:
        doc.close()
