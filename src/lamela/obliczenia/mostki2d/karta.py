"""Karta węzła: ciągłość izolacji („test ołówka” na siatce), kontrola wody i wilgoci, ocena, rysunek karty.

Wymaganie Inwestora (brief sekcja 9): odprowadzenie wody, ciągłość izolacji, mostki termiczne, rury spustowe,
hydroizolacja, paroizolacja i drenaż — dla każdego węzła katalogu:

* `ciaglosc_izolacji(w)` — zasada „linii czerwonej” sprawdzana numerycznie na siatce MOS węzła: czy istnieje droga
  po komórkach materiałów PRZEWODZĄCYCH (λ > λ_izol, domyślnie 0,12 W/(m·K) [ZAŁ]) od powierzchni wewnętrznej do
  powierzchni zewnętrznej / nieogrzewanej. Istnienie drogi = linia izolacji przerwana (mostek konstrukcyjny —
  np. płyta ciągła, ściana garażu w ociepleniu, mur fundamentowy do gruntu); zwracana jest najkrótsza droga
  (Dijkstra) i materiały na niej. Materiały izolacyjne w sensie testu: λ ≤ λ_izol (izolacje, łączniki
  termoizolacyjne, bloczki z betonu komórkowego, ramy i szyby jako materiały zastępcze).
* `kontrola_wody(wezel, model, kontekst)` — lista kontrolna: hydroizolacja / izolacja przeciwwilgociowa, paroizolacja
  i szczelność, odprowadzenie wody (spadki, obróbki, okapniki, wpusty, przelewy, rury spustowe), drenaż — z danych
  modelu (warstwy przegród — klasyfikacja `fizyka.warstwy.funkcja_warstwy`, `dachy[]`, `dzialka.odwodnienia`) oraz
  wymagań detalu (brief 9.3–9.6). Status: OK / UWAGA / BRAK / INFO.
* `ocena_wezla(w, ciag, kontrola)` — f_Rsi ≥ f_Rsi,min (W-248), ψ_oi względem wartości domyślnej PN-EN ISO 14683
  i „dobrej praktyki” (`fizyka.mostki.PSI_DOMYSLNE`), ψ_e ≤ 0,01 (kryterium „bez mostków” — informacyjnie),
  ciągłość izolacji → klasa: BEZMOSTKOWY / DOBRY / DO POPRAWY / ZŁY / NIE SPEŁNIA.
* `rysuj_karte(w, plik, ciag, ocena)` — przekrój z materiałami (λ), liniami hydro/paro/obróbek/drenażu i drogą
  mostka + mapa temperatur z izotermami i izotermą f_Rsi,min + pasek wyników.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .geometria import RODZAJE_LINII, Wezel

LAMBDA_IZOL = 0.12          # [ZAŁ] próg „materiału izolacyjnego” w teście ciągłości (beton komórkowy 400 ≈ 0,11)
PSI_BEZMOSTKOWY = 0.01      # ψ_e ≤ 0,01 W/(m·K) — kryterium „konstrukcji bez mostków” (literatura, informacyjnie) [NZW]

# odniesienia ψ_oi (domyślna PN-EN ISO 14683 zał. C, dobra praktyka) dla typów spoza `fizyka.mostki.PSI_DOMYSLNE`
PSI_REF_DODATKOWE = {"rura_spustowa": (0.10, 0.01, "wnęka w ociepleniu — rura spustowa [ZAŁ]"),
                     "sciana": (0.0, 0.0, "ściana 1D")}


# --------------------------------------------------------------------------------------------------
# Ciągłość izolacji
# --------------------------------------------------------------------------------------------------
@dataclass
class Ciaglosc:
    ciagla: bool
    sciezka: list = field(default_factory=list)       # [(x, y)] środki komórek od strony ciepłej do zimnej
    materialy: list = field(default_factory=list)     # kody materiałów wzdłuż drogi (bez powtórzeń kolejnych)
    przez_grunt: bool = False
    lam_izol: float = LAMBDA_IZOL

    @property
    def opis(self) -> str:
        if self.ciagla:
            return f"ciągła (brak drogi przez materiały o λ > {self.lam_izol:g} W/(m·K) z wnętrza na zewnątrz)"
        return ("PRZERWANA — droga mostka: " + " → ".join(self.materialy)
                + (" (wyjście przez grunt)" if self.przez_grunt else ""))


def ciaglosc_izolacji(w, lam_izol: float = LAMBDA_IZOL) -> Ciaglosc:
    """Test „ołówka” dla linii izolacji na siatce węzła. `w` — WynikWezla (siatka z rozwiązania) albo Wezel."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra
    from .siatka import klasyfikuj, siatka_dla_wezla
    if isinstance(w, Wezel):
        wezel = w
        s = siatka_dla_wezla(wezel)
        kl = klasyfikuj(wezel, s, kontrola_pustek=False)
    else:
        wezel = w.wezel
        s = w.roz_psi.model.s
        kl = w.roz_psi.model.kl
    mid, sid, lam = kl.mat_id, kl.strefa_id, kl.lam
    ny, nx = mid.shape
    # ramy i szyby (materiały zastępcze) tworzą obudowę — traktowane jak warstwa izolacyjna
    rodz_m = np.array([m.rodzaj in ("rama", "szyba") for m in kl.materialy] + [False])
    cond = (mid >= 0) & (np.nan_to_num(lam, nan=0.0) > lam_izol) & ~rodz_m[mid]
    rodz = np.array([st.rodzaj for st in wezel.strefy] + [""])
    rs = rodz[sid]                                   # −1 → ""
    warm_z, cold_z = rs == "wewn", np.isin(rs, ["zewn", "nieogrz"])

    def sasiad(maska):
        out = np.zeros_like(maska)
        out[1:, :] |= maska[:-1, :]
        out[:-1, :] |= maska[1:, :]
        out[:, 1:] |= maska[:, :-1]
        out[:, :-1] |= maska[:, 1:]
        return out

    src = cond & sasiad(warm_z)
    dst = cond & sasiad(cold_z)
    if not src.any() or not dst.any():
        return Ciaglosc(True, lam_izol=lam_izol)
    num = np.full(mid.shape, -1, np.int64)
    num[cond] = np.arange(int(cond.sum()))
    N = int(cond.sum())
    xc, yc = s.xc, s.yc
    rows, cols, vals = [], [], []
    # krawędzie poziome i pionowe między komórkami przewodzącymi
    m = cond[:, :-1] & cond[:, 1:]
    j, i = np.nonzero(m)
    rows.append(num[j, i]); cols.append(num[j, i + 1]); vals.append(xc[i + 1] - xc[i])
    m = cond[:-1, :] & cond[1:, :]
    j, i = np.nonzero(m)
    rows.append(num[j, i]); cols.append(num[j + 1, i]); vals.append(yc[j + 1] - yc[j])
    # węzeł wirtualny N — źródło (powierzchnia wewnętrzna)
    js, is_ = np.nonzero(src)
    rows.append(np.full(len(js), N)); cols.append(num[js, is_]); vals.append(np.full(len(js), 1e-9))
    r_, c_, v_ = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    G = coo_matrix((v_, (r_, c_)), shape=(N + 1, N + 1)).tocsr()
    dist, pred = dijkstra(G, directed=False, indices=N, return_predecessors=True)
    jd, id_ = np.nonzero(dst)
    kd = num[jd, id_]
    ok = np.isfinite(dist[kd])
    if not ok.any():
        return Ciaglosc(True, lam_izol=lam_izol)
    k = int(kd[ok][np.argmin(dist[kd][ok])])
    jj, ii = np.nonzero(cond)
    path = []
    while k != N and k >= 0:
        path.append(k)
        k = int(pred[k])
    path = path[::-1]
    pts = [(float(xc[ii[p]]), float(yc[jj[p]])) for p in path]
    mats, grunt = [], False
    for p in path:
        mt = kl.materialy[mid[jj[p], ii[p]]]
        grunt |= mt.rodzaj == "grunt"
        if not mats or mats[-1] != mt.kod:
            mats.append(mt.kod)
    return Ciaglosc(False, pts, mats, grunt, lam_izol)


# --------------------------------------------------------------------------------------------------
# Kontrola wody i wilgoci
# --------------------------------------------------------------------------------------------------
@dataclass
class Pozycja:
    status: str        # OK | UWAGA | BRAK | INFO
    temat: str         # hydro | paro | woda | drenaz | izolacja | rury
    tekst: str


def _funkcje_przegrody(model, kod: str | None) -> dict[str, list[str]]:
    """{funkcja: [kody materiałów]} warstw przegrody modelu (klasyfikacja `fizyka.warstwy`)."""
    if model is None or not kod:
        return {}
    try:
        from ..fizyka.warstwy import funkcja_warstwy, mat_props
        p = model.przegroda(kod)
    except Exception:
        return {}
    out: dict[str, list[str]] = {}
    for w in p.warstwy:
        f = funkcja_warstwy(mat_props(model.materialy, w.mat), {"mat": w.mat, "d": w.d})
        out.setdefault(f, []).append(w.mat)
    return out


def _przegroda_typu(model, typ: str, kody: list[str] | None = None) -> str | None:
    if model is None:
        return None
    przeg = getattr(model, "przegrody", {}) or {}
    for k in (kody or []):
        p = przeg.get(k)
        if p is not None and (p.typ if hasattr(p, "typ") else p.get("typ")) == typ:
            return k
    for k, p in przeg.items():
        if (p.typ if hasattr(p, "typ") else p.get("typ")) == typ:
            return k
    return None


def _linie_z(wezel: Wezel, fraza: str) -> bool:
    return any(fraza in ln.get("opis", "") for ln in wezel.linie)


def kontrola_wody(wezel: Wezel, model=None, kontekst: dict | None = None) -> list[Pozycja]:
    """Lista kontrolna wody i wilgoci węzła (brief 9.1, 9.3–9.6). kontekst: {'przegrody': [kody], 'dach': dict,
    'wspornik': dict, 'ciaglosc': Ciaglosc}."""
    kx = kontekst or {}
    kody = list(kx.get("przegrody") or [])
    P: list[Pozycja] = []
    add = lambda st, tm, tx: P.append(Pozycja(st, tm, tx))
    typ = wezel.typ
    raw_dz = getattr(model, "raw_dz", None) or {}
    # --- izolacja (test ołówka)
    cg: Ciaglosc | None = kx.get("ciaglosc")
    if cg is not None:
        if cg.ciagla:
            add("OK", "izolacja", "linia izolacji ciągła („test ołówka” na siatce: brak drogi przez materiały "
                                  f"o λ > {cg.lam_izol:g})")
        elif cg.przez_grunt:
            add("UWAGA", "izolacja", "linia izolacji domyka się przez grunt: " + " → ".join(cg.materialy)
                + " — ograniczyć izolacją obwodową / blokiem termicznym u podstawy muru")
        else:
            add("BRAK", "izolacja", "linia izolacji PRZERWANA: " + " → ".join(cg.materialy))
    # --- ściana: szczelność powietrzna (tynk wewn.) i warstwa zewnętrzna
    kod_sz = _przegroda_typu(model, "sciana_zewn", kody)
    fs = _funkcje_przegrody(model, kod_sz)
    if typ in ("naroze", "strop_posredni", "garaz", "oscieze", "nadproze", "podokiennik", "rura_spustowa",
               "attyka", "cokol", "wspornik", "prog") and fs:
        if "tynk" in fs or "paroizolacja" in fs or "szczelnosc" in fs:
            add("OK", "paro", f"szczelność powietrzna ściany {kod_sz}: tynk wewnętrzny ciągły "
                              f"({(fs.get('tynk') or fs.get('paroizolacja') or fs.get('szczelnosc'))[0]}) — do stropu i posadzki")
        else:
            add("BRAK", "paro", f"ściana {kod_sz}: brak warstwy szczelności powietrznej po ciepłej stronie")
    if typ == "attyka":
        kod_d = kx.get("dach", {}).get("przegroda") or _przegroda_typu(model, "stropodach", kody)
        fd = _funkcje_przegrody(model, kod_d)
        if model is not None:
            add("OK" if "paroizolacja" in fd else "BRAK", "paro",
                f"paroizolacja stropodachu {kod_d}: " + (", ".join(fd["paroizolacja"]) if "paroizolacja" in fd
                                                          else "brak w warstwach") + " — wywinięta na attykę")
            add("OK" if "hydroizolacja" in fd else "BRAK", "hydro",
                f"hydroizolacja stropodachu {kod_d}: " + (", ".join(fd["hydroizolacja"]) if "hydroizolacja" in fd
                                                           else "brak w warstwach"))
        add("BRAK" if _linie_z(wezel, "< WYMAGANE") else "OK", "hydro",
            "wywinięcie hydroizolacji na attykę ≥ 15 cm ponad warstwę wierzchnią (brief 9.4)")
        d = kx.get("dach") or ((model.dachy() or [None])[0] if model is not None else None)
        if d is not None:
            sp = d.get("spadek")
            add("OK" if (sp or 0) >= 0.02 - 1e-9 else "BRAK", "woda",
                f"spadek dachu {sp if sp is not None else 'brak'} (wymagany ≥ 2 %, izolacja spadkowa)")
            wp = d.get("wpusty") or []
            add("OK" if wp else "BRAK", "woda", f"wpusty dachowe: {len(wp)} szt." + ("" if wp else " — brak w modelu"))
            prz = d.get("przelewy_awaryjne") or d.get("rzygacze") or []
            add("OK" if prz else "BRAK", "woda", "przelewy awaryjne w attyce: " +
                (f"{len(prz)} szt." if prz else "BRAK w modelu (wymagane dla każdego pola dachu — brief 9.3; "
                                                "`dachy[].przelewy_awaryjne`)"))
            rs = d.get("rury_spustowe") or []
            add("OK" if rs else "BRAK", "rury", "rury spustowe: " +
                (", ".join(f"{r.get('id', '?')} ({r.get('trasa', '?')} → {r.get('do', '?')})" for r in rs) if rs
                 else "trasa nieokreślona w modelu (`dachy[].rury_spustowe`: szacht izolowany / zewn. z czyszczakiem, "
                      "odbiornik zbiornik/niecka)"))
        add("INFO", "woda", "obróbka korony attyki ze spadkiem ≥ 5 % do dachu i okapnikami; wpust / przelew przez "
                            "attykę — mostek punktowy χ (poza modelem 2D; kołnierz izolowany)")
    elif typ == "wspornik":
        wsp = kx.get("wspornik") or ((model.wsporniki() or [None])[0] if model is not None else None)
        kod_t = (wsp or {}).get("przegroda") or _przegroda_typu(model, "taras", kody)
        ft = _funkcje_przegrody(model, kod_t)
        if model is not None:
            add("OK" if "hydroizolacja" in ft else "BRAK", "hydro",
                f"hydroizolacja płyty {kod_t}: " + (", ".join(ft["hydroizolacja"]) if "hydroizolacja" in ft
                                                    else "brak w warstwach"))
        sp = (wsp or {}).get("spadek")
        add("OK" if sp and sp >= 0.015 else "UWAGA", "woda",
            f"spadek płyty od budynku: {sp if sp else 'nieokreślony w modelu'} (wymagany ≥ 1,5–2 %)")
        add("UWAGA", "woda", "odprowadzenie wody z krawędzi płyty (rynna / okapnik / rzygacz → rura spustowa) — "
                             "nieokreślone w modelu; obróbka czoła płyty z okapnikiem ≥ 3 cm")
        add("INFO", "hydro", "hydroizolacja wywinięta na ścianę ≥ 15 cm ponad nawierzchnię, pod cokolikiem XPS; "
                             "ciągła nad łącznikiem termoizolacyjnym")
    elif typ in ("oscieze", "nadproze", "podokiennik"):
        add("INFO", "paro", "montaż warstwowy: taśma paroszczelna od wewnątrz, paroprzepuszczalna od zewnątrz "
                            "(zasada „wewnątrz szczelniej niż na zewnątrz”)")
        if typ == "nadproze":
            add("INFO", "woda", "profil narożny z okapnikiem nad oknem; kaseta osłony — uszczelnienie i izolacja kasety")
        if typ == "podokiennik":
            add("OK" if _linie_z(wezel, "okapnik") else "BRAK", "woda",
                "parapet zewnętrzny: spadek ≥ 5 %, okapnik ≥ 3 cm przed licem, zaślepki boczne, taśma pod parapetem")
    elif typ == "prog" and "grunt" not in wezel.dane:
        kod_t = _przegroda_typu(model, "taras", kody)
        ft = _funkcje_przegrody(model, kod_t)
        if model is not None and "łącznik" in wezel.dane:
            add("OK" if "hydroizolacja" in ft else "BRAK", "hydro",
                f"hydroizolacja tarasu/balkonu {kod_t}: " + (", ".join(ft["hydroizolacja"]) if "hydroizolacja" in ft
                                                             else "brak w warstwach"))
        add("INFO", "woda", "próg: hydroizolacja / taśma EPDM wprowadzona pod ramę, spadek ≥ 1,5–2 % od budynku, "
                            "odwodnienie liniowe przy progu bezbarierowym (brief 9.4)")
    elif typ in ("cokol", "prog"):
        kod_p = _przegroda_typu(model, "podloga_na_gruncie", kody)
        fp = _funkcje_przegrody(model, kod_p)
        zal_pod = "[ZAŁ]" in str(wezel.dane.get("warstwy podłogi — źródło", ""))
        if zal_pod:
            add("INFO", "hydro", "warstwy płyty przyjęte w wariancie porównawczym [ZAŁ]: hydroizolacja pod płytą "
                                 "(na XPS) wywinięta na krawędź płyty i połączona z uszczelnieniem strefy cokołu")
        elif model is not None:
            iz = fp.get("przeciwwilgociowa", []) + fp.get("hydroizolacja", [])
            add("OK" if iz else "BRAK", "hydro", f"izolacja przeciwwilgociowa podłogi na gruncie {kod_p}: " +
                (", ".join(iz) if iz else "BRAK w warstwach przegrody (np. papa / folia PE na płycie podkładowej, "
                                          "połączona z izolacją poziomą pod murem)"))
        add("OK", "hydro", "izolacja pionowa fundamentu i izolacja obwodowa XPS (nienasiąkliwa) — w modelu węzła")
        add("BRAK" if _linie_z(wezel, "< WYMAGANE") else "OK", "hydro",
            "strefa cokołu ≥ 30 cm nad terenem (uszczelnienie, tynk mozaikowy)")
        odw = raw_dz.get("odwodnienia") or []
        tp = (raw_dz.get("teren") or {}).get("punkty_projektowane")
        add("OK" if odw else "BRAK", "drenaz", "odwodnienie przy budynku (`dzialka.odwodnienia`: opaska żwirowa / drenaż "
            "opaskowy / odwodnienie liniowe): " + (", ".join(str(o.get("typ")) for o in odw) if odw else
                                                  "brak w modelu działki — decyzja o drenażu wg badań gruntu "
                                                  "(brief 9.6) do udokumentowania"))
        add("OK" if tp else "UWAGA", "woda", "spadek terenu ≥ 2 % od budynku na 1,5–2 m: " +
            ("rzędne projektowane w modelu" if tp else "brak rzędnych projektowanych terenu w modelu działki"))
        if typ == "prog":
            add("INFO", "woda", "próg bezbarierowy: odwodnienie liniowe przed drzwiami, hydroizolacja pod próg")
    elif typ == "rura_spustowa":
        dachy = model.dachy() if model is not None else []
        rs = [r for d in dachy for r in (d.get("rury_spustowe") or [])]
        add("OK" if rs else "BRAK", "rury", "rury spustowe w modelu: " + (f"{len(rs)} szt." if rs else
                                                                          "brak (`dachy[].rury_spustowe`)"))
        add("UWAGA", "izolacja", "wnęka w ETICS pocienia izolację (ψ > 0) — zalecana rura przed licem na obejmach "
                                 "dystansowych albo w izolowanym szachcie wewnętrznym")
        add("INFO", "rury", "czyszczak / osadnik nad terenem, podłączenie do zbiornika retencyjnego / niecki "
                            "(PN-EN 12056-3), kolano z wylotem nad opaską żwirową zabronione przy ścianie")
    elif typ == "garaz":
        add("INFO", "paro", "ściana dom–garaż: szczelność na spaliny (WT § 106 ust. 1) — tynk ciągły, uszczelnione "
                            "przejścia instalacji, drzwi z samozamykaczem i uszczelką")
    return P


# --------------------------------------------------------------------------------------------------
# Ocena
# --------------------------------------------------------------------------------------------------
KLASY = {  # klasa: (kolor tła, opis)
    "BEZMOSTKOWY": ("#1a7f37", "ψ_e ≤ 0,01 W/(m·K), f_Rsi spełnione, izolacja ciągła"),
    "DOBRY": ("#2d8a4e", "ψ_oi ≤ dobra praktyka, f_Rsi spełnione"),
    "DO POPRAWY": ("#b7791f", "ψ_oi > dobra praktyka lub linia izolacji domyka się przez grunt"),
    "ZŁY": ("#c2410c", "ψ_oi > wartość domyślna PN-EN ISO 14683 lub izolacja przerwana konstrukcją"),
    "NIE SPEŁNIA": ("#b91c1c", "f_Rsi < f_Rsi,min — ryzyko pleśni (WT zał. 2 pkt 2.2)"),
}


def psi_odniesienia(wezel: Wezel) -> tuple[float, float, str, str] | None:
    """(ψ_oi domyślna, ψ_oi dobra praktyka, opis, klucz) dla typu węzła (`fizyka.mostki.PSI_DOMYSLNE`)."""
    typ = wezel.typ
    try:
        from ..fizyka.mostki import PSI_DOMYSLNE
    except Exception:   # pragma: no cover
        PSI_DOMYSLNE = {}
    klucz = {"naroze": "naroznik_wypukly", "strop_posredni": "strop_posredni", "attyka": "attyka",
             "oscieze": "oscieze", "nadproze": "oscieze", "podokiennik": "oscieze", "prog": "oscieze",
             "cokol": "sciana_grunt", "garaz": "polaczenie_nieogrz"}.get(typ, typ)
    if typ == "prog":
        klucz = ("sciana_grunt" if "grunt" in wezel.dane else
                 "plyta_wspornikowa_lacznik" if "łącznik" in wezel.dane else "oscieze")
    if typ == "wspornik":
        # węzeł projektowy „płyta wspornikowa” wymaga łącznika (brief 9.2) — odniesienie: z łącznikiem
        klucz = "plyta_wspornikowa_lacznik"
    if klucz in PSI_DOMYSLNE:
        d, dp, op = PSI_DOMYSLNE[klucz][:3]
        return float(d), float(dp), op, klucz
    if klucz in PSI_REF_DODATKOWE:
        d, dp, op = PSI_REF_DODATKOWE[klucz]
        return d, dp, op, klucz
    return None


def ocena_wezla(w, ciag: Ciaglosc | None = None, kontrola: list[Pozycja] | None = None) -> dict[str, Any]:
    p = w.psi_glowne
    ref = psi_odniesienia(w.wezel)
    uz = []
    if not w.fRsi_ok:
        kl = "NIE SPEŁNIA"
        uz.append(f"f_Rsi = {w.f['f_Rsi']:.3f} < {w.fRsi_min}")
    else:
        kl = "DOBRY"
        if ciag is not None and not ciag.ciagla and not ciag.przez_grunt:
            kl = "ZŁY"
            uz.append("izolacja przerwana: " + " → ".join(ciag.materialy))
        bez = p is not None and p.psi_e <= PSI_BEZMOSTKOWY and (ciag is None or ciag.ciagla)
        if ref is not None and p is not None and not bez:
            # ψ ≤ 0,01 W/(m·K) — pomijalne (tolerancja porównania z wartościami tabelarycznymi)
            d, dp, _, _ = ref
            if p.psi_oi > max(d, PSI_BEZMOSTKOWY) + 1e-9:
                kl = "ZŁY"
                uz.append(f"ψ_oi = {p.psi_oi:.3f} > domyślna {d:.2f}")
            elif p.psi_oi > max(dp, PSI_BEZMOSTKOWY) + 1e-9 and kl != "ZŁY":
                kl = "DO POPRAWY"
                uz.append(f"ψ_oi = {p.psi_oi:.3f} > dobra praktyka {dp:.2f}")
        if kl == "DOBRY" and ciag is not None and not ciag.ciagla:
            kl = "DO POPRAWY"
            uz.append("izolacja domyka się przez grunt")
        if kl == "DOBRY" and bez:
            kl = "BEZMOSTKOWY"
    braki = [k for k in (kontrola or []) if k.status == "BRAK" and k.temat != "izolacja"]
    uwagi = [k for k in (kontrola or []) if k.status == "UWAGA" and k.temat != "izolacja"]
    return {"klasa": kl, "kolor": KLASY[kl][0], "uzasadnienie": "; ".join(uz) or KLASY[kl][1], "ref": ref,
            "braki_wody": len(braki), "uwagi_wody": len(uwagi)}


# --------------------------------------------------------------------------------------------------
# Rysunek karty
# --------------------------------------------------------------------------------------------------
STYLE_LINII = {   # rodzaj: (kolor, szer., styl) — kolory zasady „4 linii” (brief 9.1)
    "hydro": ("#1f5fd6", 2.2, "-"),
    "przeciwwilg": ("#1f5fd6", 1.8, (0, (5, 2))),
    "paro": ("#12a150", 2.2, "-"),
    "tasma_wewn": ("#12a150", 3.0, "-"),
    "tasma_zewn": ("#1f5fd6", 3.0, (0, (1.2, 1.2))),
    "obrobka": ("#222222", 1.8, "-"),
    "woda": ("#0891b2", 1.6, "-"),
    "drenaz": ("#8b5a2b", 1.6, (0, (4, 2))),
    "rura": ("#6b7280", 1.8, "-"),
}
KOLOR_STREF = {"wewn": "#fde8e4", "zewn": "#e3eefb", "nieogrz": "#fbf3d5"}


def _kolor_mat(m) -> str:
    if m.kolor:
        return m.kolor
    if m.rodzaj == "szyba":
        return "#cfe8f7"
    if m.rodzaj == "rama":
        return "#f1f1f1"
    if m.lam <= 0.06:
        return "#f3e7a8"
    return "#cfcac0"


def _patch(geom, **kw):
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    verts, codes = [], []
    for poly in getattr(geom, "geoms", [geom]):
        if poly.is_empty or not hasattr(poly, "exterior"):
            continue
        for ring in [poly.exterior] + list(poly.interiors):
            xy = np.asarray(ring.coords)
            verts += xy.tolist()
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
    if not verts:
        return None
    return PathPatch(MPath(verts, codes), **kw)


def _widok(wezel: Wezel, asp_max: float = 1.25):
    """Okno rysunku karty: `wezel.widok` (albo obrys materiałów), dla węzłów wysokich poszerzone symetrycznie do
    proporcji wys./szer. ≤ asp_max (czytelny układ dwóch paneli)."""
    if wezel.widok:
        x0, y0, x1, y1 = wezel.widok
    else:
        from shapely.ops import unary_union
        x0, y0, x1, y1 = unary_union([o.wielobok for o in wezel.obszary]).bounds
    if (y1 - y0) > asp_max * (x1 - x0):
        d = ((y1 - y0) / asp_max - (x1 - x0)) / 2
        x0, x1 = x0 - d, x1 + d
    return (x0, y0, x1, y1)


def rysuj_przekroj(ax, wezel: Wezel, ciag: Ciaglosc | None = None, legenda_ax=None):
    """Przekrój z materiałami (wypełnienie kolorem materiału; izolacje λ ≤ 0,06 — kreskowanie czerwone = linia
    izolacji), strefy powietrza z opisem θ, linie schematyczne (`Wezel.linie`) i droga mostka (test ołówka)."""
    import matplotlib as mpl
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from shapely.geometry import box
    from shapely.ops import unary_union
    widok = _widok(wezel)
    vb = box(*widok)
    mpl.rcParams["hatch.linewidth"] = 0.5
    # strefy powietrza: dopełnienie materiałów w widoku, kolor strefy najbliższej
    mats_u = unary_union([o.wielobok for o in wezel.obszary])
    wolne = vb.difference(mats_u)
    for part in getattr(wolne, "geoms", [wolne]):
        if part.is_empty or part.area < 1e-6:
            continue
        st = min(wezel.strefy, key=lambda z: z.wielobok.distance(part))
        pt = _patch(part, facecolor=KOLOR_STREF.get(st.rodzaj, "#f4f4f4"), edgecolor="none", zorder=0)
        if pt is not None:
            ax.add_patch(pt)
        minx, miny, maxx, maxy = part.bounds
        if part.area > 0.02 * vb.area and min(maxx - minx, maxy - miny) > 0.10 * min(widok[2] - widok[0],
                                                                                      widok[3] - widok[1]):
            from shapely.ops import polylabel
            try:
                rp = polylabel(part.buffer(0) if part.geom_type == "Polygon" else part.representative_point(),
                               tolerance=0.005)
            except Exception:   # pragma: no cover
                rp = part.representative_point()
            ax.text(rp.x, rp.y, f"{st.nazwa}\nθ = {st.theta:g} °C", ha="center", va="center", fontsize=7.5,
                    color="#444444", zorder=8, style="italic")
    uzyte: dict[str, Any] = {}
    for k, o in enumerate(wezel.obszary):
        g = o.wielobok.intersection(vb.buffer(0.02))
        if g.is_empty:
            continue
        m = o.mat
        izol = m.lam <= 0.06 and m.rodzaj not in ("szyba", "rama")
        kw = dict(facecolor=_kolor_mat(m), edgecolor="#d62728" if izol else "#333333",
                  lw=0.35, hatch="////" if izol else ("...." if m.rodzaj == "grunt" else None), zorder=1 + k * 1e-3)
        pt = _patch(g, **kw)
        if pt is not None:
            ax.add_patch(pt)
            uzyte.setdefault(m.kod, m)
    # linie schematyczne
    rodz_uz = []
    for ln in wezel.linie:
        kol, lw, ls = STYLE_LINII[ln["rodzaj"]]
        xy = np.asarray(ln["xy"])
        if ln.get("alt"):
            ls = (0, (3, 2))
        if ln["rodzaj"] == "woda":
            ax.annotate("", xy=xy[-1], xytext=xy[0], zorder=7,
                        arrowprops=dict(arrowstyle="-|>", color=kol, lw=lw, mutation_scale=11))
        else:
            ax.plot(xy[:, 0], xy[:, 1], color=kol, lw=lw, ls=ls, zorder=6, solid_capstyle="butt")
        if ln["rodzaj"] not in rodz_uz:
            rodz_uz.append(ln["rodzaj"])
    if ciag is not None and not ciag.ciagla and ciag.sciezka:
        xy = np.asarray(ciag.sciezka)
        ax.plot(xy[:, 0], xy[:, 1], color="#d62728", lw=2.6, ls=(0, (2, 1.5)), zorder=9)
        ax.plot(xy[[0, -1], 0], xy[[0, -1], 1], ls="none", marker="X", ms=9, mfc="#d62728", mec="white", zorder=10)
    ax.set_xlim(widok[0], widok[2])
    ax.set_ylim(widok[1], widok[3])
    ax.set_aspect("equal")
    ax.tick_params(labelsize=7)
    ax.set_xlabel("x [m]", fontsize=8)
    ax.set_ylabel("y [m]", fontsize=8)
    # legenda: materiały (λ) + linie
    h = []
    for m in uzyte.values():
        izol = m.lam <= 0.06 and m.rodzaj not in ("szyba", "rama")
        nz = (m.nazwa or m.kod)
        nz = nz if len(nz) <= 34 else nz[:33] + "…"
        h.append(Patch(facecolor=_kolor_mat(m), edgecolor="#d62728" if izol else "#333333", lw=0.5,
                       hatch="////" if izol else ("...." if m.rodzaj == "grunt" else None),
                       label=f"{m.kod} — {nz}, λ = {m.lam:.3g}"))
    for r in rodz_uz:
        kol, lw, ls = STYLE_LINII[r]
        h.append(Line2D([], [], color=kol, lw=lw, ls=ls, label=RODZAJE_LINII[r]))
    if any(ln.get("alt") for ln in wezel.linie):
        h.append(Line2D([], [], color=STYLE_LINII["rura"][0], lw=1.8, ls=(0, (3, 2)), label="wariant zalecany"))
    if ciag is not None and not ciag.ciagla:
        h.append(Line2D([], [], color="#d62728", lw=2.6, ls=(0, (2, 1.5)), marker="X", ms=6,
                        label="droga mostka — przerwa linii izolacji"))
    tgt = legenda_ax or ax
    tgt.legend(handles=h, loc="upper left", fontsize=6.6, ncol=2, frameon=False, handlelength=2.4,
               borderaxespad=0.0, columnspacing=1.2)


def rysuj_temperature(ax, w, fig=None):
    s = w.roz_psi.model.s
    T = np.ma.masked_invalid(w.roz_psi.T)
    widok = _widok(w.wezel)
    th = list(w.theta.values())
    lo, hi = min(th), max(th)
    pc = ax.pcolormesh(s.x, s.y, T, cmap="coolwarm", vmin=lo, vmax=hi, shading="flat", zorder=1, rasterized=True)
    krok = 2.0
    lev = np.arange(math.ceil(lo / krok) * krok, hi + 1e-9, krok)
    cs = ax.contour(s.xc, s.yc, T, levels=lev, colors="k", linewidths=0.4, zorder=2)
    lab = [v for v in lev if abs(v % 4) < 1e-9]
    ax.clabel(cs, lab, fontsize=6, fmt="%.0f °C", inline_spacing=2)
    lim = w.f["theta_e"] + w.fRsi_min * (w.f["theta_i"] - w.f["theta_e"])
    Tf = np.ma.masked_invalid(w.roz_f.T)
    ax.contour(w.roz_f.model.s.xc, w.roz_f.model.s.yc, Tf, levels=[lim], colors="#9d174d", linewidths=1.4,
               linestyles="--", zorder=4)
    ax.contour(s.xc, s.yc, T, levels=[0.0], colors="#1e3a8a", linewidths=1.0, zorder=3)
    from shapely.geometry import box as _box
    vb = _box(*widok).buffer(0.05)
    for o in w.wezel.obszary:
        g = o.wielobok.intersection(vb)
        for part in getattr(g, "geoms", [g]):
            if part.is_empty or not hasattr(part, "exterior"):
                continue
            for rg in [part.exterior] + list(part.interiors):
                xy = np.asarray(rg.coords)
                ax.plot(xy[:, 0], xy[:, 1], color="#333333", lw=0.3, zorder=3, alpha=0.7)
    ax.plot([w.f["x"]], [w.f["y"]], marker="o", mfc="none", mec="#9d174d", mew=1.8, ms=10, zorder=6)
    ax.annotate(f"θ_si,min = {w.f['theta_si_min']:.1f} °C\n(R_si = 0,25)", (w.f["x"], w.f["y"]),
                xytext=(14, -26), textcoords="offset points", fontsize=7, color="#9d174d", zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
    ax.set_xlim(widok[0], widok[2])
    ax.set_ylim(widok[1], widok[3])
    ax.set_aspect("equal")
    ax.tick_params(labelsize=7)
    ax.set_xlabel("x [m]", fontsize=8)
    if fig is not None:
        cb = fig.colorbar(pc, ax=ax, shrink=0.75, pad=0.02)
        cb.set_label("θ [°C] (R_s wg ISO 6946)", fontsize=7.5)
        cb.ax.tick_params(labelsize=7)
    return lim


def rysuj_karte(w, plik: str | Path, ciag: Ciaglosc | None = None, ocena: dict | None = None,
                kontrola: list[Pozycja] | None = None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    wz = w.wezel
    widok = _widok(wz)
    asp = (widok[3] - widok[1]) / max(widok[2] - widok[0], 1e-9)
    H_pl = float(np.clip(6.2 * asp, 3.6, 7.2))
    H_f = H_pl + 3.6
    fig = plt.figure(figsize=(15.0, H_f), dpi=130)
    gs = fig.add_gridspec(3, 2, height_ratios=[H_pl, 1.95, 0.75], hspace=0.22, wspace=0.10,
                          left=0.05, right=0.97, top=1.0 - 0.75 / H_f, bottom=0.02)
    ax1, ax2 = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    axl, axl2, axw = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1]), fig.add_subplot(gs[2, :])
    for a in (axl, axl2, axw):
        a.axis("off")
    rysuj_przekroj(ax1, wz, ciag, legenda_ax=axl)
    ax1.set_title("Przekrój — materiały (λ [W/(m·K)]), hydro / paro / obróbki / odwodnienie", fontsize=9)
    lim = rysuj_temperature(ax2, w, fig)
    ax2.set_title("Rozkład temperatury, izotermy co 2 K", fontsize=9)
    axl2.legend(handles=[Line2D([], [], color="k", lw=0.6, label="izotermy co 2 K (opis co 4 K)"),
                         Line2D([], [], color="#1e3a8a", lw=1.0, label="izoterma 0 °C"),
                         Line2D([], [], color="#9d174d", lw=1.4, ls="--",
                                label=f"θ = {lim:.1f} °C ↔ f_Rsi,min = {w.fRsi_min} (R_si = 0,25; ISO 13788)"),
                         Line2D([], [], ls="none", marker="o", mfc="none", mec="#9d174d", mew=1.8, ms=8,
                                label="θ_si,min — punkt krytyczny powierzchni wewn.")],
                loc="upper left", fontsize=7, frameon=False, borderaxespad=0.0)
    if kontrola:
        ikony = {"OK": "✓", "UWAGA": "!", "BRAK": "✗", "INFO": "i"}
        kol = {"OK": "#1a7f37", "UWAGA": "#b7791f", "BRAK": "#b91c1c", "INFO": "#555555"}
        wazne = [k for k in kontrola if k.status in ("BRAK", "UWAGA")][:5]
        y = 0.40
        axl2.text(0.0, y + 0.08, "Woda / wilgoć / ciągłość — pozycje do działania:" if wazne else
                  "Woda / wilgoć / ciągłość: bez braków w danych modelu", fontsize=7.5, weight="bold",
                  transform=axl2.transAxes, va="bottom")
        for k in wazne:
            t = k.tekst if len(k.tekst) <= 120 else k.tekst[:119] + "…"
            axl2.text(0.0, y, f"{ikony[k.status]} {t}", fontsize=6.8, color=kol[k.status], transform=axl2.transAxes,
                      va="top")
            y -= 0.085
    p = w.psi_glowne
    oc = ocena or {}
    ref = oc.get("ref")
    t1 = (f"ψ_e = {p.psi_e:+.3f}   ψ_i = {p.psi_i:+.3f}   ψ_oi = {p.psi_oi:+.3f} W/(m·K)   (L_2D = {p.L2D:.4f})"
          if p else "ψ — n/d")
    t2 = (f"θ_si,min = {w.f['theta_si_min']:.2f} °C   f_Rsi = {w.f['f_Rsi']:.3f} "
          f"({'≥' if w.fRsi_ok else '<'} {w.fRsi_min})")
    if ref:
        t2 += f"   ψ_oi odniesienia: domyślna {ref[0]:.2f} / dobra praktyka {ref[1]:.2f}"
    t3 = "izolacja: " + (ciag.opis if ciag is not None else "—")
    axw.text(0.0, 0.92, t1, fontsize=10, weight="bold", transform=axw.transAxes, va="top")
    axw.text(0.0, 0.55, t2, fontsize=9, transform=axw.transAxes, va="top")
    axw.text(0.0, 0.22, t3 if len(t3) <= 150 else t3[:149] + "…", fontsize=8,
             color="#b91c1c" if ciag is not None and not ciag.ciagla else "#1a7f37", transform=axw.transAxes,
             va="top")
    if oc:
        axw.text(1.0, 0.92, f" OCENA: {oc['klasa']} ", fontsize=12, weight="bold", color="white", ha="right",
                 va="top", transform=axw.transAxes, bbox=dict(boxstyle="round,pad=0.35", fc=oc["kolor"], ec="none"))
        uz = oc["uzasadnienie"]
        axw.text(1.0, 0.42, uz if len(uz) <= 90 else uz[:89] + "…", fontsize=7.5, ha="right", va="top",
                 transform=axw.transAxes, color="#333333")
    fig.suptitle(f"{wz.id} — {wz.nazwa}", fontsize=12, weight="bold", x=0.05, y=1.0 - 0.12 / H_f, ha="left",
                 va="top")
    plik = Path(plik)
    plik.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plik)
    plt.close(fig)
    return str(plik)


# --------------------------------------------------------------------------------------------------
# Raport katalogu kart
# --------------------------------------------------------------------------------------------------
@dataclass
class KartaWezla:
    w: Any                       # WynikWezla
    ciag: Ciaglosc
    kontrola: list
    ocena: dict
    png: str = ""


def karta_wezla(w, model=None, kontekst: dict | None = None, plik_png: str | Path | None = None) -> KartaWezla:
    """Ciągłość + kontrola wody + ocena (+ rysunek karty) dla wyniku `oblicz_wezel`."""
    c = ciaglosc_izolacji(w)
    kx = dict(kontekst or {})
    kx["ciaglosc"] = c
    kt = kontrola_wody(w.wezel, model, kx)
    oc = ocena_wezla(w, c, kt)
    png = rysuj_karte(w, plik_png, c, oc, kt) if plik_png else ""
    return KartaWezla(w, c, kt, oc, png)


def _f(x, n=3, znak=False):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    s = f"{x:+.{n}f}" if znak else f"{x:.{n}f}"
    return s.replace(".", ",").replace("-", "−")


def _izol_krotko(c: Ciaglosc) -> str:
    if c.ciagla:
        return "ciągła"
    return "przez grunt" if c.przez_grunt else "**PRZERWANA**"


def tabela_kart(karty: list[KartaWezla], rel=lambda p: p) -> str:
    L = ["| węzeł | nazwa | ψ_e | ψ_i | ψ_oi | θ_si,min [°C] | f_Rsi | izolacja | woda / wilgoć* | ocena |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k in karty:
        p = k.w.psi_glowne
        wd = (f"{k.ocena['braki_wody']} ✗ / {k.ocena['uwagi_wody']} !" if (k.ocena['braki_wody'] or
                                                                            k.ocena['uwagi_wody']) else "✓")
        L.append(f"| [{k.w.wezel.id}](#{k.w.wezel.id.lower()}) | {k.w.wezel.nazwa} | {_f(p.psi_e, 3, True)} | "
                 f"{_f(p.psi_i, 3, True)} | {_f(p.psi_oi, 3, True)} | {_f(k.w.f['theta_si_min'], 2)} | "
                 f"{_f(k.w.f['f_Rsi'], 3)}{'' if k.w.fRsi_ok else ' **✗**'} | {_izol_krotko(k.ciag)} | {wd} | "
                 f"**{k.ocena['klasa']}** |")
    return "\n".join(L)


def raport_kart(karty: list[KartaWezla], plik: str | Path, tytul: str, wstep: str = "", walidacja_txt: str = "",
                porownania: list | None = None, dlugosci: dict | None = None, szczegoly: str | None = None,
                pominiete: list[str] | None = None) -> str:
    plik = Path(plik)
    rel = lambda p: str(Path(p).relative_to(plik.parent)) if p else ""
    ti = karty[0].w.f["theta_i"] if karty else 20.0
    te = karty[0].w.f["theta_e"] if karty else -18.0
    fmin = karty[0].w.fRsi_min if karty else 0.72
    L = [f"# {tytul}", "", wstep, "",
         "**Cel** (brief sekcja 9 — wymaganie Inwestora): potwierdzenie symulacją numeryczną ciągłości izolacji i braku "
         "ryzyka pleśni w węzłach oraz kontrola odprowadzenia wody, hydroizolacji, paroizolacji, rur spustowych i drenażu.",
         "",
         "**Metoda.** Model 2D metodą objętości skończonych (`lamela.obliczenia.mostki2d`) wg PN-EN ISO 10211:2017: "
         "płaszczyzny odcięcia ≥ max(1 m; 3·d), R_se = 0,04, R_si = 0,13 / 0,10 / 0,17 (ISO 6946) do strumieni i ψ; "
         f"R_si = 0,25 (ramy/szyby 0,13) do θ_si i f_Rsi (PN-EN ISO 13788); θ_i = {_f(ti, 0)} °C, θ_e = {_f(te, 0)} °C; "
         "grunt λ = 2,0 W/(m·K), podłoga wg PN-EN ISO 13370 z B′ = A/(0,5·P). Siatka zagęszczana przy granicach "
         "materiałów i podwajana do zmiany strumienia < 1 % i ψ ≤ max(1 %; 0,001 W/(m·K)); bilans energii < 10⁻⁴. "
         "ψ_e — wymiary zewnętrzne, ψ_i — wewnętrzne (PN-EN ISO 14683), ψ_oi — wewnętrzne całkowite (system projektu, "
         "H_TB). Walidacja solvera: " + (walidacja_txt or "patrz `projekt/08_obliczenia/mostki2d/walidacja_ISO10211.md`")
         + ".", "",
         f"**Ciągłość izolacji („test ołówka”, zasada linii czerwonej)** — sprawdzana na siatce każdego węzła: "
         f"szukana jest droga z powierzchni wewnętrznej na zewnętrzną / do strefy nieogrzewanej wyłącznie przez "
         f"materiały o λ > {LAMBDA_IZOL:g} W/(m·K) [ZAŁ] (ramy i szyby traktowane jak obudowa). Brak drogi = linia "
         f"izolacji ciągła; droga istnieje = mostek konstrukcyjny (na karcie czerwona linia przerywana ✕–✕); droga "
         f"kończąca się w gruncie = izolacja domyka się przez grunt (typowe dla ław — ocena „do poprawy”).", "",
         "**Ocena:** " + "; ".join(f"**{k}** — {v[1]}" for k, v in KLASY.items()) + ". Odniesienia ψ_oi: "
         "wartość domyślna PN-EN ISO 14683 zał. C i „dobra praktyka” z `fizyka.mostki.PSI_DOMYSLNE` [NZW]; "
         f"f_Rsi,min = {fmin} (W-248, WT zał. 2 pkt 2.2). Kryterium „bez mostków” ψ_e ≤ 0,01 W/(m·K) — informacyjne.", "",
         "**Rysunki (zasada „4 linii”, brief 9.1):** izolacja — kreskowanie czerwone; hydroizolacja / izolacja "
         "przeciwwodna — niebieska ciągła, przeciwwilgociowa — niebieska przerywana; paroizolacja / szczelność "
         "powietrzna (tynk wewn., taśmy wewn.) — zielona; taśmy / uszczelnienia zewnętrzne — niebieska kropkowana; "
         "obróbki, parapety, okapniki — czarna; spływ wody — strzałka turkusowa; drenaż / opaska żwirowa — brązowa; "
         "rura spustowa — szara. Membrany, taśmy i obróbki są pomijalne cieplnie (poza modelem 2D, tylko na rysunku) — "
         "z wyjątkiem warstw przegród modelu (EPDM, paroizolacja, hydroizolacja pionowa), które są w obliczeniu.", "",
         "## Tabela zbiorcza", "", tabela_kart(karty), "",
         "\\* woda / wilgoć: liczba pozycji listy kontrolnej ✗ BRAK / ! UWAGA (bez pozycji „izolacja”) — dane do "
         "uzupełnienia w modelu lub rozwiązania do pokazania na detalu; ✓ — bez braków.", ""]
    if pominiete:
        L += ["Pominięte wpisy sekcji `wezly`: " + "; ".join(pominiete), ""]
    idk = {k.w.wezel.id: k for k in karty}
    if porownania:
        L += ["## Porównanie wariantów", ""]
        for tyt, ids, kom in porownania:
            ks = [idk[i] for i in ids if i in idk]
            if len(ks) < 2:
                continue
            L += [f"### {tyt}", "", "| węzeł | wariant | ψ_e | ψ_oi | f_Rsi | izolacja | ocena |", "|---|---|---|---|---|---|---|"]
            for k in ks:
                p = k.w.psi_glowne
                L.append(f"| {k.w.wezel.id} | {k.w.wezel.nazwa} | {_f(p.psi_e, 3, True)} | {_f(p.psi_oi, 3, True)} | "
                         f"{_f(k.w.f['f_Rsi'], 3)} | {_izol_krotko(k.ciag)} | **{k.ocena['klasa']}** |")
            a, b = ks[0], ks[-1]
            pa, pb = a.w.psi_glowne, b.w.psi_glowne
            L += ["", f"Różnica {b.w.wezel.id} względem {a.w.wezel.id}: Δψ_oi = {_f(pb.psi_oi - pa.psi_oi, 3, True)} "
                      f"W/(m·K), Δf_Rsi = {_f(b.w.f['f_Rsi'] - a.w.f['f_Rsi'], 3, True)}, "
                      f"Δθ_si,min = {_f(b.w.f['theta_si_min'] - a.w.f['theta_si_min'], 2, True)} K — {kom}.", ""]
    # zbiorcza lista działań (woda / wilgoć / ciągłość)
    zb: dict[tuple[str, str], list[str]] = {}
    for k in karty:
        for poz in k.kontrola:
            if poz.status in ("BRAK", "UWAGA"):
                zb.setdefault((poz.status, poz.tekst), []).append(k.w.wezel.id)
    if zb:
        L += ["## Woda, wilgoć, ciągłość — pozycje do uzupełnienia", "",
              "Zestawienie pozycji ✗ BRAK / ! UWAGA z list kontrolnych wszystkich węzłów (dane modelu i działki oraz "
              "wymagania detalu — brief 9.3–9.6).", "", "| status | pozycja | węzły |", "|---|---|---|"]
        for (st, tx), ids in sorted(zb.items(), key=lambda x: (x[0][0] != "BRAK", x[0][1])):
            L.append(f"| {'✗ BRAK' if st == 'BRAK' else '! UWAGA'} | {tx} | {', '.join(ids)} |")
        L.append("")
    if dlugosci:
        from .wyniki import zestawienie_HTB
        H, wiersze = zestawienie_HTB([k.w for k in karty], dlugosci, "oi")
        if wiersze:
            L += ["## H_TB z wartości symulowanych (ψ_oi)", "", "| węzeł | nazwa | ψ_oi [W/(m·K)] | l_oi [m] | ψ·l [W/K] |",
                  "|---|---|---|---|---|"]
            for r in wiersze:
                L.append(f"| {r[0]} | {r[1]} | {_f(r[2], 3, True)} | {_f(r[3], 2)} | {_f(r[4], 2, True)} |")
            L += ["", f"**H_TB = Σ ψ_oi·l_oi = {_f(H, 2)} W/K** (węzły liniowe wg modelu; warianty porównawcze bez "
                      "długości nie są sumowane; mostki punktowe χ — poza zakresem 2D).", ""]
    L += ["## Karty węzłów", ""]
    ik = {"OK": "✓", "UWAGA": "!", "BRAK": "✗", "INFO": "i"}
    for k in karty:
        wz, p = k.w.wezel, k.w.psi_glowne
        L += [f"### {wz.id}", "", f"**{wz.nazwa}** — ocena **{k.ocena['klasa']}** ({k.ocena['uzasadnienie']})", ""]
        if k.png:
            L += [f"![{wz.id} — karta węzła]({rel(k.png)})", ""]
        ref = k.ocena.get("ref")
        L += [f"* ψ_e = {_f(p.psi_e, 3, True)}, ψ_i = {_f(p.psi_i, 3, True)}, ψ_oi = {_f(p.psi_oi, 3, True)} W/(m·K); "
              f"L_2D = {_f(p.L2D, 4)} W/(m·K)" + (f"; odniesienie ψ_oi: domyślna {_f(ref[0], 2)}, dobra praktyka "
                                                    f"{_f(ref[1], 2)} ({ref[2]})" if ref else ""),
              f"* θ_si,min = {_f(k.w.f['theta_si_min'], 2)} °C, f_Rsi = {_f(k.w.f['f_Rsi'], 3)} "
              f"({'≥' if k.w.fRsi_ok else '<'} {k.w.fRsi_min} — {'brak ryzyka pleśni i kondensacji powierzchniowej' if k.w.fRsi_ok else 'RYZYKO PLEŚNI'})"
              + (f"; rama/szyba f_Rsi = {_f(k.w.f['f_Rsi_okno'], 3)} (informacyjnie)" if "f_Rsi_okno" in k.w.f else ""),
              f"* izolacja: {k.ciag.opis}",
              f"* siatka: {k.w.siatki[-1][1]} komórek, zmiana Φ przy podwojeniu {_f(100 * k.w.zmiana, 3)} %, "
              f"bilans {k.w.bilans:.1e}", "",
              "| | temat | pozycja listy kontrolnej |", "|---|---|---|"]
        for poz in k.kontrola:
            L.append(f"| {ik[poz.status]} {poz.status} | {poz.temat} | {poz.tekst} |")
        L.append("")
        for u in wz.uwagi:
            L.append(f"*Uwaga:* {u}")
        if wz.linie:
            L.append("*Na rysunku:* " + "; ".join(sorted({ln["opis"] for ln in wz.linie if ln.get("opis")})) + ".")
        if k.w.wykresy:
            L.append("")
            L.append("Wykresy szczegółowe: " + ", ".join(f"[{n}]({rel(v)})" for n, v in k.w.wykresy.items())
                     + (f"; dane wejściowe, warunki brzegowe, siatka, elementy flankujące — "
                        f"[{Path(szczegoly).name}]({rel(szczegoly)})" if szczegoly else ""))
        L.append("")
    L += ["## Ograniczenia", "",
          "* Modele 2D (mostki liniowe). Mostki punktowe χ (wpusty i przelewy w attyce, konsole, kotwy, narożniki 3D, "
          "przejścia rur) — poza zakresem; wymagają modelu 3D lub deklaracji wyrobu.",
          "* Łącznik termoizolacyjny, okna, profile progowe — DANE PRZYKŁADOWE (do zastąpienia deklaracjami wyrobów).",
          "* Ocena pleśni kryterium f_Rsi (stan ustalony); transport wilgoci w przegrodach — metoda Glasera w "
          "obliczeniach fizyki budowli (`05_wilgotnosc.md`).",
          "* Linie hydro/paro/obróbek/drenażu na rysunkach są schematem wymagań detalu, nie rysunkiem wykonawczym.", ""]
    txt = "\n".join(L)
    plik.parent.mkdir(parents=True, exist_ok=True)
    plik.write_text(txt, encoding="utf-8")
    return txt
