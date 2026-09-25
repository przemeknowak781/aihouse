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

from .formaty import odmiana
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


def _ile_widokow(tytul: str) -> int:
    """Liczba widoków na arkuszu wg tytułu: oznaczenia przekrojów „A-A”, „B-B” (każde osobno); tytuł w liczbie
    mnogiej bez oznaczeń („ELEWACJE”, „PRZEKROJE”) — co najmniej 2; „ELEWACJE N, S, E, W” — liczba kierunków."""
    t = tytul.split("(")[0]
    n = len(re.findall(r"\b([A-Z])\s*[-–]\s*\1\b", t))
    kier = re.search(r"ELEWACJ\w*\s+((?:[NSEW]|PŁN|PŁD|WSCH|ZACH)\w*(?:\s*[,i]\s*\w+)+)", t, re.I)
    if kier:
        n = max(n, len(re.split(r"\s*[,i]\s*", kier.group(1).strip())))
    if n == 0 and re.search(r"\b(PRZEKROJE|ELEWACJE|RZUTY)\b", t, re.I):
        n = 2
    return max(1, n)


def _etykieta_wzorca(w: str) -> str:
    """Wzorzec regex → czytelna etykieta do raportu (bez flag i klas znaków)."""
    w = re.sub(r"\(\?-?i:", "", w)
    w = re.sub(r"\\w\*|\\w\+|\\b|[()?]", "", w)
    return w.replace("\\", "")


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


def _wiersz_tabliczki(slowa, etykieta: str) -> str | None:
    """Tekst wiersza metryki (na prawo od komórki FUNKCJA = ``etykieta``); None — brak wiersza."""
    for w in slowa:
        if w[4].lower().rstrip(":") == etykieta.lower():
            y = (w[1] + w[3]) / 2
            h = max(w[3] - w[1], 1.0)
            reszta = [v for v in slowa if v[0] > w[2] and abs((v[1] + v[3]) / 2 - y) < 0.8 * h
                      and v[0] - w[2] < 400]
            t = " ".join(v[4] for v in sorted(reszta, key=lambda v: v[0]))
            if t.startswith("(wsp"):                       # wiersz współprojektanta — szukaj dalej
                continue
            return t
    return None


def _tabliczki(doc, an) -> tuple[str, str]:
    """Metryki arkuszy (RPB § 10 ust. 1 pkt 3; W-305, W-320): wiersz „Projektant” niepusty (dane albo
    [DO UZUPEŁNIENIA]); wiersz „Sprawdzający” — osoba albo „nie dotyczy (art. 20 ust. 3 pkt 2 PB)”."""
    zle, n = [], 0
    for i, p in enumerate(doc):
        if an["a4"][i]:
            continue
        slowa = p.get_text("words")
        if not any("UPRAWNIE" in w[4].upper() for w in slowa):
            continue                                   # arkusz bez tabliczki lamela.draft (np. zastępczy)
        n += 1
        pr = _wiersz_tabliczki(slowa, "Projektant")
        sp = _wiersz_tabliczki(slowa, "Sprawdzający")
        if pr is not None and not re.search(r"\w{3,}", pr):
            zle.append(f"s. {i + 1}: pusty wiersz „Projektant”")
        if sp is not None and not re.search(r"\w{3,}", sp):
            zle.append(f"s. {i + 1}: pusty wiersz „Sprawdzający”")
    if not n:
        return "OK", "brak arkuszy z tabliczką lamela.draft"
    return ("BRAK" if zle else "OK"), ("; ".join(zle[:6]) + (f" … (+{len(zle) - 6})" if len(zle) > 6 else "")
                                       if zle else f"{n} {odmiana(n, 'tabliczka', 'tabliczki', 'tabliczek')} z wypełnioną metryką")


def _spec(nazwa, doc, sciezka, an, lista, el_info) -> tuple[str, str]:
    if nazwa == "nazwa_pliku":
        ok, opis = sprawdz_nazwe(Path(sciezka).name, lista.get("nazwa_pliku"))
        if ok and lista.get("symbol") and f"_{lista['symbol']}_" not in Path(sciezka).name:
            return "BRAK", f"symbol specjalności w nazwie ≠ {lista['symbol']}"
        return ("OK" if ok else "BRAK"), opis
    if nazwa == "rozmiar":
        mb = Path(sciezka).stat().st_size / 1_000_000
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
    if nazwa == "tabliczki":
        return _tabliczki(doc, an)
    if nazwa == "stan_modelu":
        # weryfikacja PT (K-1): tom wygenerowany z bieżącego stanu modelu; ten sam skrót we wszystkich tomach
        from .dane import stan_modelu, RE_STAN_MODELU
        biez = stan_modelu()["skrot"]
        w_tomie = sorted({m.group(1).lower() for t in an["teksty"] for m in RE_STAN_MODELU.finditer(t)})
        if not w_tomie:
            return "OSTRZEŻENIE", f"brak znacznika „stan modelu: SHA-256 …” (bieżący model: {biez})"
        if w_tomie != [biez]:
            return "BRAK", f"tom ze stanu modelu {', '.join(w_tomie)} ≠ bieżący model {biez} — wygenerować ponownie"
        return "OK", f"stan modelu SHA-256 {biez} = bieżący model"
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
            if poz.get("brak_gdy") and not any(k in sz for k in ("spec", "skala_max", "tytulowa", "zakladki", "tekst",
                                                                   "rysunki")):
                # pozycja „negatywna”: BRAK, gdy w treści elementu jest znacznik niedomkniętej analizy
                # (wzorce z (?-i:…) są wrażliwe na wielkość liter — np. „NIESPEŁNIONY” w tabeli warunków)
                tekst_el = info["tekst"] if info else " ".join(an["teksty"])
                tr = [(w, len(re.findall(w.replace(" ", r"\s+"), tekst_el, flags=re.I))) for w in poz["brak_gdy"]]
                tr = [(w, n) for w, n in tr if n]
                st = ("BRAK" if ob else "OSTRZEŻENIE") if tr else "OK"
                opis = ((poz.get("brak_opis") or "znaczniki niedomkniętej analizy") + ": "
                        + ", ".join(f"„{_etykieta_wzorca(w)}” ×{n}" for w, n in tr)) if tr else \
                    "brak znaczników niedomkniętej analizy"
                pozycje.append(Pozycja(status=st, szczegoly=opis, **base))
                continue
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
                    ile = sum(_ile_widokow(t) for t in zakres["rysunki"] if rx.search(t))
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
                # treść zastępcza (rejestr E.1): pozycja jest, ale jej sekcja zawiera znacznik wskazany na liście
                zast_tr = _szukaj(poz.get("uzupelnic_gdy") or [], zakres["tekst"])
                if zast_tr:
                    st = "DO UZUPEŁNIENIA"
                    szczeg.append(poz.get("uzupelnic_opis") or "treść zastępcza ze znacznikiem [DO UZUPEŁNIENIA] / "
                                  "[DOKUMENT ZEWNĘTRZNY]")
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
                                  rozmiar_mb=sciezka.stat().st_size / 1_000_000, strony=doc.page_count)
    finally:
        doc.close()
