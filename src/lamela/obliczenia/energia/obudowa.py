"""Obudowa cieplna budynku z modelu: U wszystkich elementów (PN-EN ISO 6946 / 13370 / 10077-1), mostki (H_TB),
zacienienie okien, sprawdzenie g (WT zał. 2 pkt 2.1) i kontrola ciągłości warstw przegród zewnętrznych.

Konfiguracja z modelu (opcjonalna sekcja `energia` w budynek.yaml — lista pól: `lamela/obliczenia/README.md`):
  energia.grunt: {typ: piasek|glina|skala, lambda, izolacja_obwodowa: {typ: pionowa|pozioma, D, d_n, lam_n}, psi_wf, G_w}
  energia.wezly_wyniki: ścieżka do wyników symulacji ISO 10211 ({id: {psi, f_rsi, dlugosc}})
  energia.psi_wariant: domyslna | dobra_praktyka
  stolarka.<symbol>: {wyrob: <klucz z dane/wyroby_przykladowe.yaml>, U_g, U_f, psi_g, b_f, b_s, g_n, U_D}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..fizyka import grunt as G
from ..fizyka import mostki as MB
from ..fizyka import okna as OK
from ..fizyka.u_przegrody import WynikU, oblicz_u, poprawki_domyslne, u_przegrody_modelu, warstwy_przegrody
from ..fizyka.warstwy import WynikCiaglosci, sprawdz_ciaglosc
from ..wspolne import NZW, ROOT, ZAL, Zalozenia, wym
from .bryla import Bryla, Element, buduj_bryle
from .klimat import klimat_miesieczny


@dataclass
class Obudowa:
    m: Any
    bryla: Bryla
    u: dict                          # (uklad, rola) → WynikU
    okna: dict                       # id elementu → WynikOkno
    grunt: G.WynikGrunt | None
    grunt_nieogrz: G.WynikGrunt | None
    wezly: list
    H_TB: float
    zacienienie: dict                # id okna → wynik zacienienie_miesieczne
    g_spr: list
    ciaglosc: list
    U_elem: dict                     # id elementu → U [W/(m²K)]
    zal: Zalozenia
    cfg: dict = field(default_factory=dict)

    def U(self, e: Element) -> float:
        return self.U_elem[e.id]

    @property
    def A_obudowy(self) -> float:
        return sum(e.A for e in self.bryla.elementy_obudowy())

    def H_elem(self, e: Element) -> float:
        return e.A * self.U_elem[e.id]


def cfg_energia(m) -> dict:
    raw = getattr(m, "raw", {}) or {}
    e = raw.get("energia")
    return e if isinstance(e, dict) else {}


def oblicz_obudowe(m, *, wyniki_symulacji: dict | None = None, wariant_psi: str | None = None,
                   zacienienie: bool = True, zal: Zalozenia | None = None) -> Obudowa:
    zal = zal or Zalozenia()
    cfg = cfg_energia(m)
    br = buduj_bryle(m)
    U: dict = {}
    U_elem: dict = {}
    k = klimat_miesieczny()

    def u_dla(e: Element) -> WynikU | None:
        key = (e.uklad or e.przegroda, e.rola)
        if key in U:
            return U[key]
        if e.warstwy is not None:
            pop = poprawki_domyslne(e.rola, e.warstwy, m.materialy, zal)
            w = oblicz_u(e.warstwy, m.materialy, rola=e.rola, poprawki=pop, kod=str(e.uklad), nazwa=e.uwagi or str(e.uklad))
        elif e.przegroda and m.przegroda(e.przegroda) is not None:
            w = u_przegrody_modelu(m, e.przegroda, e.rola, zal=zal, dach=e.dach)
        else:
            return None
        U[key] = w
        return w

    # --- grunt ---
    gcfg = cfg.get("grunt") or {}
    iz = gcfg.get("izolacja_obwodowa")
    izol = G.IzolacjaKrawedziowa(iz.get("typ", "pionowa"), float(iz["D"]), float(iz["d_n"]), float(iz["lam_n"]),
                                 iz.get("opis", "")) if isinstance(iz, dict) else None
    wg = wn = None
    for og, dane in ((True, br.grunt), (False, br.grunt_nieogrz)):
        if dane["A"] <= 0 or dane["P"] <= 0:
            continue
        prz = dane["przegrody"][0] if dane["przegrody"] else None
        if prz is None:
            continue
        wu = oblicz_u(warstwy_przegrody(m, prz), m.materialy, rola="podloga_grunt", kod=prz,
                      nazwa=m.przegroda(prz).nazwa)
        U[(prz, "podloga_grunt" if og else "podloga_grunt_nieogrz")] = wu
        th = br.theta_srednia() if og else 5.0
        r = G.oblicz_grunt(dane["A"], dane["P"], dane["w"], wu.R_f, grunt=gcfg.get("typ", "piasek"),
                           lam=gcfg.get("lambda"), izolacja=izol if og else None,
                           psi_wf=float(gcfg.get("psi_wf") or 0.0), theta_int=th, G_w=float(gcfg.get("G_w", 1.0)),
                           klimat_mies=list(k.theta_e), zal=zal if og else None)
        wu.U = r.U
        wu.U_c = r.U
        wu.uwagi.append(f"U_equiv wg PN-EN ISO 13370: A = {r.A:.2f} m², P = {r.P:.2f} m, B' = {r.B:.2f} m, "
                        f"d_t = {r.d_t:.2f} m".replace(".", ","))
        if og:
            wg = r
        else:
            wn = r
            wu.U_max = wu.U_cel = None
    # --- stolarka ---
    stol = (getattr(m, "raw", {}) or {}).get("stolarka") or {}
    okna = {}
    for e in br.elementy:
        if e.rodzaj in ("okno", "drzwi", "brama"):
            o = e.otwor
            dane = OK.dane_stolarki(o.symbol, o.typ, stol)
            rola = None
            if e.rodzaj == "drzwi":
                rola = "drzwi"
            if e.rodzaj == "brama" or not br.pomieszczenia[e.pom].ogrzewane:
                rola = "brama" if e.rodzaj == "brama" else "drzwi_nieogrz"
            wo = OK.u_okna(o.szer, o.wys, dane, n_kw=OK.liczba_kwater(o.typ, o.szer, o.raw.get("kwatery")),
                           rola=rola)
            if rola == "drzwi_nieogrz":
                wo.U_max = None
                wo.U_cel = None
            okna[e.id] = wo
            U_elem[e.id] = wo.U_w
    rozm: dict = {}
    for e in br.elementy:
        if e.id in okna:
            rozm.setdefault(okna[e.id].symbol, set()).add((round(e.otwor.szer, 3), round(e.otwor.wys, 3)))
    for sy, r_ in rozm.items():
        if len(r_) > 1:
            br.ostrzezenia.append(f"stolarka: symbol {sy} występuje w różnych wymiarach "
                                  f"({', '.join(f'{a:.2f}×{b:.2f}' for a, b in sorted(r_))}) — ujednolicić zestawienie stolarki")
    if any(d.dane.status and "PRZYK" in d.dane.status for d in okna.values()):
        zal.dodaj("Stolarka: U_g, U_f, Ψ_g, szerokości ram, g_n — dane przykładowe typowych wyrobów "
                  "(dane/wyroby_przykladowe.yaml); do zastąpienia deklaracjami wybranego producenta", "[DANE PRZYKŁADOWE – FIKCYJNE]")
    # --- elementy nieprzezroczyste ---
    for e in br.elementy:
        if e.id in U_elem:
            continue
        if e.rola == "podloga_grunt":
            og = br.pomieszczenia[e.pom].ogrzewane
            r = wg if og else wn
            U_elem[e.id] = r.U if r else 0.3
            continue
        w = u_dla(e)
        U_elem[e.id] = w.U if w is not None else 0.0
        if w is None and br.pomieszczenia[e.pom].ogrzewane and e.sasiad != br.pomieszczenia[e.pom].id:
            br.ostrzezenia.append(f"{e.pom}/{e.id}: brak układu warstw ({e.rola}) — U = 0 (sprawdzić model)")
    # --- mostki ---
    sym = wyniki_symulacji
    if sym is None and cfg.get("wezly_wyniki"):
        p = Path(cfg["wezly_wyniki"])
        p = p if p.is_absolute() else ROOT / p
        if p.exists():
            sym = MB.wczytaj_wyniki_symulacji(p)
    wezly = MB.wezly_z_modelu(m, sym, wezly_auto=br.wezly_auto,
                              wariant_domyslny=wariant_psi or cfg.get("psi_wariant", "domyslna"), zal=zal)
    Htb = MB.h_tb(wezly)
    # --- zacienienie i g ---
    zac = {}
    gs = []
    for e in br.elementy:
        if e.rodzaj != "okno" or e.sasiad != "zewn" or not br.pomieszczenia[e.pom].ogrzewane:
            continue
        wo = okna[e.id]
        F_lato = None
        if zacienienie and e.zacienienie:
            r = OK.zacienienie_miesieczne(e.azymut, e.dlugosc, e.wysokosc, okap=e.zacienienie.get("okap"),
                                          lamele=e.zacienienie.get("lamele"))
            zac[e.id] = r
            F_lato = r["F_sh_lato"]
        gs.append(OK.sprawdz_g(e.id, wo.symbol, e.azymut, wo.A_w, wo.g_n, wo.U_g, e.otwor.oslona, F_lato))
    if zac:
        zal.dodaj("Zacienienie stałe (okapy — płyty wysunięte, lamele) — F_sh z danych godzinowych TMY Poznań i położenia "
                  "Słońca; model izotropowy nieba, ρ_g = 0,2", ZAL, "PN-EN ISO 52016-1 p. 6.5.13 (idea); lamela.sun")
    # --- ciągłość warstw ---
    rola_map = {"sciana_zewn": "sciana_zewn", "sciana_nieogrz": "sciana_nieogrz", "dach": "dach",
                "strop_zewn": "strop_zewn", "strop_nieogrz": "strop_nieogrz", "strop_nieogrz_gora": "strop_nieogrz",
                "podloga_grunt": "podloga_grunt"}
    cg: dict = {}
    for e in br.elementy_obudowy():
        rola = rola_map.get(e.rola)
        if rola is None:
            continue
        key = (e.uklad or e.przegroda, rola)
        if key not in cg:
            if e.warstwy is not None:
                ws, kod, nazwa = e.warstwy, str(e.uklad), e.uwagi or str(e.uklad)
            elif e.przegroda and m.przegroda(e.przegroda) is not None:
                ws, kod, nazwa = warstwy_przegrody(m, e.przegroda), e.przegroda, m.przegroda(e.przegroda).nazwa
            else:
                continue
            cg[key] = sprawdz_ciaglosc(kod, nazwa, ws, m.materialy, rola)
        cg[key].elementy.append(f"{e.pom}:{e.id}")
    return Obudowa(m, br, U, okna, wg, wn, wezly, Htb, zac, gs, list(cg.values()), U_elem, zal, cfg)


def raport_ciaglosc(wyniki: list[WynikCiaglosci], uwagi_wezlow: list | None = None) -> str:
    from ..wspolne import naglowek_raportu, tabela_md
    s = [naglowek_raportu("Ciągłość warstw przegród zewnętrznych kubatury ogrzewanej (zasada „4 linii”)",
                          "brief sekcja 9 pkt 1 i 5 (wymaganie Inwestora 25.09.2026); WT § 321, zał. 2 pkt 2.2.5, 2.3.1; "
                          "WT § 106 ust. 1 (garaż–dom); § 315–317 (izolacje przeciwwilgociowe i przeciwwodne)",
                          ["Linie: izolacja termiczna (czerwona), szczelność powietrzna/paroizolacja (zielona), "
                           "hydroizolacja (niebieska), warstwa zewnętrzna/wiatroizolacja. Kontrola na poziomie przegród "
                           "(obecność i kolejność warstw); ciągłość w węzłach — detale i audyt rysunków."])]
    rows = []
    for w in wyniki:
        br_ = "; ".join(u.opis for u in w.braki) or "—"
        ost = "; ".join(u.opis for u in w.uwagi if u.poziom == "OSTRZEZENIE") or "—"
        rows.append([w.kod, w.nazwa[:45], w.rola, len(w.elementy), "✔" if w.ok else "✘", br_, ost])
    s.append(tabela_md(["Przegroda", "Nazwa", "Rola", "Elementów", "Wynik", "Braki", "Ostrzeżenia"], rows, "lllrlll"))
    s.append("")
    for w in wyniki:
        s.append(f"* **{w.kod}** ({w.rola}): warstwy — " + ", ".join(f"{k} [{f}] {d * 100:.1f} cm" for k, f, d in w.warstwy))
        for u in w.uwagi:
            if u.poziom == "INFO":
                s.append(f"  * informacja: {u.opis}")
    if uwagi_wezlow:
        s.append("")
        s.append("Węzły (połączenia przegród):")
        for u in uwagi_wezlow:
            s.append(f"* [{u.poziom}] {u.opis}")
    s.append("")
    return "\n".join(s)
