"""Mostki cieplne: Ψ, χ, H_TB i f_Rsi węzłów — PN-EN ISO 14683:2017 (wartości domyślne) / wyniki PN-EN ISO 10211.

Hierarchia źródeł Ψ i f_Rsi węzła (od najważniejszego):
  1. wynik symulacji numerycznej wg PN-EN ISO 10211:2017 — słownik `{id_wezla: {"psi": …, "f_rsi": …, "dlugosc": …}}`
     (solver 2D `lamela.obliczenia.mostki2d` — osobny moduł; tu wyłącznie przyjmowanie wyników),
  2. deklaracja producenta wyrobu (łącznik termoizolacyjny płyt wspornikowych, konsola) — DANE PRZYKŁADOWE,
  3. wartość domyślna wg PN-EN ISO 14683:2017 zał. C — **tylko jako rozwiązanie awaryjne** [NZW: wartości zał. C nie
     zostały zweryfikowane na egzemplarzu normy (rejestr R6-32); dla wsporników R6 zaleca Ψ numeryczne]; wartości
     uzgodnione z tabelą orientacyjną `mostki2d.geometria.PSI_DOMYSLNE_14683` (Ψ_i ≡ Ψ_oi; strop pośredni Ψ_e);
     wariant „dobra_praktyka” — typowe wartości dla ciągłej izolacji zewnętrznej (literatura) [NZW].
System wymiarów: wewnętrzne całkowite (Ψ_oi) — zgodnie z `energia.bryla`.
H_TB = Σ l_k·Ψ_k + Σ χ_j (PN-EN ISO 14683 p. 4; PN-EN ISO 13789 p. 6.?).
f_Rsi węzła — z symulacji (PN-EN ISO 10211) albo deklaracji; brak — status „do wyznaczenia”.
Wymaganie: f_Rsi ≥ f_Rsi,wym (PN-EN ISO 13788 rozdz. 5; WT zał. 2 pkt 2.2.1–2.2.3; rejestr W-248).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import yaml

from ..wspolne import NZW, PRZYKL, ZAL, Zalozenia, fmt, naglowek_raportu, ok, tabela_md, wyrob

# Ψ_oi [W/(m·K)] — (domyślna PN-EN ISO 14683 zał. C [NZW], dobra praktyka [NZW]); opis
PSI_DOMYSLNE: dict[str, tuple[float, float, str]] = {
    "attyka": (0.75, 0.20, "stropodach–ściana zewnętrzna z attyką (izolacja attyki z 3 stron)"),
    "okap": (0.75, 0.25, "stropodach z płytą wysuniętą (okap) — płyta przechodzi przez izolację"),
    "naroznik_wypukly": (0.15, 0.06, "narożnik zewnętrzny ścian (izolacja zewnętrzna)"),
    "naroznik_wklesly": (-0.10, -0.10, "narożnik wewnętrzny ścian"),
    "strop_posredni": (0.00, 0.00, "strop pośredni – ściana zewnętrzna z izolacją ciągłą (ETICS); Ψ_oi = Ψ_e (wys. „od podłogi do podłogi”)"),
    "strop_zewn_krawedz": (0.60, 0.15, "strop nad powietrzem zewnętrznym – ściana (wspornik bryły)"),
    "oscieze": (0.10, 0.04, "ościeża/nadproża/parapety — okno w warstwie izolacji („ciepły montaż”)"),
    "sciana_grunt": (0.80, 0.15, "ściana zewnętrzna – podłoga na gruncie / płyta fundamentowa (cokół)"),
    "plyta_wspornikowa": (0.95, 0.95, "płyta wspornikowa (balkon/taras/okap) przechodząca przez izolację bez łącznika"),
    "plyta_wspornikowa_lacznik": (0.30, 0.15, "płyta wspornikowa z łącznikiem termoizolacyjnym"),
    "polaczenie_nieogrz": (0.20, 0.10, "połączenie przegród dom–garaż nieogrzewany (ściana/strop)"),
    "slup": (0.30, 0.10, "słup/rama przechodząca przez izolację (rama boksu, słup stalowy)"),
}
# aliasy typów węzłów (np. klucze katalogu `mostki2d.geometria.PSI_DOMYSLNE_14683`, skrócone nazwy w modelu)
ALIASY_TYPOW = {"R_attyka": "attyka", "C_naroze_zewn": "naroznik_wypukly", "naroze": "naroznik_wypukly",
                "naroznik": "naroznik_wypukly", "IF_strop": "strop_posredni", "GF_cokol": "sciana_grunt",
                "cokol": "sciana_grunt", "W_oscieze": "oscieze", "B_balkon": "plyta_wspornikowa",
                "wspornik": "plyta_wspornikowa_lacznik", "garaz": "polaczenie_nieogrz", "okap_plyty": "okap"}
# typy, dla których Ψ_oi = Ψ_e (wymiar pionowy „od podłogi do podłogi”); pozostałe: Ψ_oi = Ψ_i
PSI_OI_Z_E = ("strop_posredni", "plyta_wspornikowa", "plyta_wspornikowa_lacznik")

CHI_DOMYSLNE: dict[str, tuple[float, str]] = {
    "konsola_lamel": (0.010, "konsola mocowania lamel (przekładka termiczna)"),
    "przejscie_instalacji": (0.005, "przejście instalacji przez przegrodę zewnętrzną (mankiet)"),
    "kotwa": (0.010, "punktowa kotwa stalowa przez izolację"),
}


@dataclass
class Wezel:
    id: str
    typ: str
    nazwa: str
    dlugosc: float = 0.0             # [m] (węzły liniowe)
    liczba: float = 0.0              # [szt.] (węzły punktowe)
    psi: float | None = None         # [W/(m·K)]
    chi: float | None = None         # [W/K]
    f_rsi: float | None = None
    zrodlo_psi: str = ""
    zrodlo_frsi: str = ""
    status: str = ""
    przegrody: list[str] = field(default_factory=list)
    uwagi: str = ""

    @property
    def H(self) -> float:
        return (self.dlugosc * (self.psi or 0.0)) + (self.liczba * (self.chi or 0.0))


def wczytaj_wyniki_symulacji(plik) -> dict:
    """Wyniki symulacji ISO 10211 (JSON/YAML): {id: {psi, f_rsi, dlugosc?, …}} lub lista z polem id."""
    p = Path(plik)
    d = json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else yaml.safe_load(p.read_text(encoding="utf-8"))
    if isinstance(d, list):
        return {str(x["id"]): x for x in d}
    if isinstance(d, dict) and "wezly" in d and isinstance(d["wezly"], (list, dict)):
        return wczytaj_wyniki_symulacji_dict(d["wezly"])
    return {str(k): v for k, v in (d or {}).items()}


def wczytaj_wyniki_symulacji_dict(d) -> dict:
    if isinstance(d, list):
        return {str(x["id"]): x for x in d}
    return {str(k): v for k, v in d.items()}


def psi_z_symulacji(s: dict, typ: str) -> tuple[float | None, str]:
    """Ψ w systemie wymiarów wewnętrznych całkowitych z wyniku symulacji: 'psi_oi' > ('psi_e' dla stropów pośrednich
    i płyt wspornikowych | 'psi_i' dla pozostałych) > 'psi'."""
    if s.get("psi_oi") is not None:
        return float(s["psi_oi"]), "Ψ_oi"
    if typ in PSI_OI_Z_E and s.get("psi_e") is not None:
        return float(s["psi_e"]), "Ψ_e ≡ Ψ_oi"
    if s.get("psi_i") is not None:
        return float(s["psi_i"]), "Ψ_i ≡ Ψ_oi"
    if s.get("psi") is not None:
        return float(s["psi"]), "Ψ"
    return None, ""


def wyniki_z_mostki2d(wyniki, dlugosci: dict | None = None) -> dict:
    """Adapter wyników `lamela.obliczenia.mostki2d` (lista WynikWezla) → {id: {psi_e, psi_i, f_rsi, dlugosc}}."""
    out = {}
    for w in wyniki:
        wz = getattr(w, "wezel", None)
        wid = str(getattr(wz, "id", None) or getattr(w, "id", ""))
        pg = getattr(w, "psi_glowne", None)
        f = getattr(w, "f", {}) or {}
        d = {"zrodlo": "symulacja PN-EN ISO 10211 (mostki2d)"}
        if pg is not None:
            d["psi_e"] = float(getattr(pg, "psi_e"))
            d["psi_i"] = float(getattr(pg, "psi_i"))
        if f.get("f_Rsi") is not None:
            d["f_rsi"] = float(f["f_Rsi"])
        if dlugosci and wid in dlugosci:
            d["dlugosc"] = float(dlugosci[wid])
        out[wid] = d
    return out


def psi_domyslne(typ: str, wariant: str = "domyslna") -> tuple[float | None, str]:
    if typ in PSI_DOMYSLNE:
        a, b, opis = PSI_DOMYSLNE[typ]
        v = a if wariant == "domyslna" else b
        zr = ("PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback)" if wariant == "domyslna"
              else "typowa wartość dla ciągłej izolacji zewnętrznej (literatura)")
        return v, f"{zr} {NZW}"
    return None, ""


def wezly_z_modelu(m=None, wyniki_symulacji: dict | None = None, *, wezly_auto: Sequence[dict] = (),
                   wariant_domyslny: str = "domyslna", zal: Zalozenia | None = None) -> list[Wezel]:
    """Katalog węzłów: `wezly` z modelu (SCHEMAT_MODELU.md p. 6) albo węzły wygenerowane z geometrii (`bryla`).

    Ψ/f_Rsi: wyniki symulacji (klucz = id węzła) > deklaracja łącznika (typ plyta_wspornikowa_lacznik, konsola_lamel)
    > wartość domyślna (`wariant_domyslny`: 'domyslna' — PN-EN ISO 14683 zał. C, 'dobra_praktyka')."""
    sym = wyniki_symulacji or {}
    raw = []
    if m is not None and isinstance(getattr(m, "raw", None), dict) and isinstance(m.raw.get("wezly"), list):
        raw = m.raw["wezly"]
    out: list[Wezel] = []
    src = raw if raw else [dict(id=f"AUTO-{i + 1:02d}", nazwa=w.get("opis", w["typ"]), **w) for i, w in enumerate(wezly_auto)]
    for w in src:
        wid = str(w.get("id"))
        typ = str(w.get("typ", "inny"))
        typ = ALIASY_TYPOW.get(typ, typ)
        wz = Wezel(id=wid, typ=typ, nazwa=str(w.get("nazwa", typ)), dlugosc=float(w.get("dlugosc") or 0.0),
                   liczba=float(w.get("liczba") or 0.0), przegrody=[str(x) for x in (w.get("przegrody") or [])])
        s = sym.get(wid)
        if s:
            if s.get("dlugosc") is not None:
                wz.dlugosc = float(s["dlugosc"])
            psi, rodz = psi_z_symulacji(s, typ)
            if psi is not None:
                wz.psi = psi
                wz.zrodlo_psi = str(s.get("zrodlo", "symulacja PN-EN ISO 10211 (mostki2d)")) + f" ({rodz})"
            if s.get("chi") is not None:
                wz.chi = float(s["chi"])
                wz.zrodlo_psi = str(s.get("zrodlo", "symulacja PN-EN ISO 10211 (mostki2d)"))
            if s.get("f_rsi") is not None:
                wz.f_rsi = float(s["f_rsi"])
                wz.zrodlo_frsi = str(s.get("zrodlo", "symulacja PN-EN ISO 10211 (mostki2d)"))
            wz.status = "symulacja"
        if w.get("psi") is not None and wz.psi is None:
            wz.psi = float(w["psi"])
            wz.zrodlo_psi = str(w.get("zrodlo_psi", "model (wartość wpisana)"))
        if w.get("f_rsi") is not None and wz.f_rsi is None:
            wz.f_rsi = float(w["f_rsi"])
            wz.zrodlo_frsi = str(w.get("zrodlo_frsi", "model (wartość wpisana)"))
        if wz.psi is None and wz.chi is None:
            if typ == "plyta_wspornikowa_lacznik":
                L = wyrob("laczniki", "wspornik_termiczny")
                wz.psi = float(L.get("psi", 0.15))
                wz.zrodlo_psi = f"deklaracja łącznika — {L.get('zrodlo', '')} {PRZYKL}"
                if wz.f_rsi is None and L.get("f_Rsi") is not None:
                    wz.f_rsi = float(L["f_Rsi"])
                    wz.zrodlo_frsi = wz.zrodlo_psi
                wz.status = wz.status or "deklaracja (przykładowa)"
            elif typ in CHI_DOMYSLNE:
                wz.chi, opis = CHI_DOMYSLNE[typ]
                wz.zrodlo_psi = f"wartość przykładowa — {opis} {PRZYKL}"
                wz.status = wz.status or "przykładowa"
            else:
                v, zr = psi_domyslne(typ, wariant_domyslny)
                if v is None:
                    v, zr = 0.10, f"brak typu w katalogu — przyjęto 0,10 W/(m·K) {ZAL}"
                wz.psi = v
                wz.zrodlo_psi = zr
                wz.status = wz.status or "domyślna"
        if wz.f_rsi is None:
            wz.zrodlo_frsi = "do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d)"
        out.append(wz)
    if zal is not None:
        if any(w.status == "domyślna" for w in out):
            zal.dodaj("Ψ węzłów bez wyników symulacji — wartości domyślne (fallback) " +
                      ("PN-EN ISO 14683:2017 zał. C" if wariant_domyslny == "domyslna" else "„dobra praktyka”") +
                      " w systemie wymiarów wewnętrznych całkowitych (Ψ_oi); do zastąpienia wynikami ISO 10211", NZW)
        if not raw:
            zal.dodaj("Katalog węzłów wygenerowany automatycznie z geometrii modelu (brak sekcji `wezly`) — długości "
                      "sumaryczne wg typów", ZAL)
    return out


def h_tb(wezly: Sequence[Wezel]) -> float:
    """H_TB = Σ l·Ψ + Σ χ [W/K]."""
    return sum(w.H for w in wezly)


def sprawdz_frsi(wezly: Sequence[Wezel], f_rsi_wym: float) -> list[dict]:
    out = []
    for w in wezly:
        out.append({"id": w.id, "opis": f"{w.nazwa} ({w.typ})", "f_Rsi": w.f_rsi,
                    "zrodlo": w.zrodlo_frsi, "ok": None if w.f_rsi is None else w.f_rsi >= f_rsi_wym - 1e-9})
    return out


def raport_mostki(wezly: Sequence[Wezel], f_rsi_wym: float | None = None, A_obudowy: float | None = None,
                  zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu("Mostki cieplne — Ψ, χ, H_TB, f_Rsi węzłów",
                          "PN-EN ISO 14683:2017-09 (zał. C — wartości domyślne, wyłącznie rozwiązanie awaryjne); "
                          "PN-EN ISO 10211:2017-09 (symulacje — moduł mostki2d); PN-EN ISO 13788:2013 rozdz. 5; "
                          "WT zał. 2 pkt 2.2.1–2.2.3",
                          ["H_TB = Σ l_k·Ψ_k + Σ χ_j; system wymiarów: wewnętrzne całkowite (Ψ_oi).",
                           "Kolumna „Źródło Ψ” wskazuje: symulację ISO 10211, deklarację producenta (dane przykładowe) albo "
                           "wartość domyślną [NZW]."])]
    rows = []
    for w in wezly:
        rows.append([w.id, w.nazwa[:60], w.typ, fmt(w.dlugosc, 2) if w.dlugosc else (fmt(w.liczba, 0) + " szt." if w.liczba else "—"),
                     fmt(w.psi, 3) if w.psi is not None else (f"χ={fmt(w.chi, 3)}" if w.chi is not None else "—"),
                     fmt(w.H, 2), w.zrodlo_psi, fmt(w.f_rsi, 2) if w.f_rsi is not None else "—",
                     ok(None if (w.f_rsi is None or f_rsi_wym is None) else w.f_rsi >= f_rsi_wym - 1e-9)])
    s.append(tabela_md(["Węzeł", "Opis", "Typ", "l [m] / n", "Ψ [W/(mK)]", "H [W/K]", "Źródło Ψ", "f_Rsi",
                        f"f_Rsi ≥ {fmt(f_rsi_wym, 2) if f_rsi_wym else '—'}"], rows, "lllrrrlrl"))
    s.append("")
    H = h_tb(wezly)
    s.append(f"**H_TB = {fmt(H, 2)} W/K**" + (f"; ΔU_TB = H_TB/A_obudowy = {fmt(H / A_obudowy, 3)} W/(m²K) "
                                              f"(A_obudowy = {fmt(A_obudowy, 1)} m²)." if A_obudowy else "."))
    brak = [w.id for w in wezly if w.f_rsi is None]
    if brak:
        s.append("")
        s.append(f"Węzły bez f_Rsi (wymagana symulacja PN-EN ISO 10211 — moduł mostki2d): {', '.join(brak)}.")
    s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
