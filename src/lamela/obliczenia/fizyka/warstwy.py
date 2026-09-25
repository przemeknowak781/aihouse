"""Warstwy przegród: właściwości materiałów, klasyfikacja funkcji warstw i kontrola „ciągłości warstw”.

Kontrola ciągłości (wymaganie Inwestora z 25.09.2026 — brief sekcja 9 pkt 1 i 5, zasada „4 linii”):
każda przegroda zewnętrzna kubatury ogrzewanej musi mieć
  1. izolację termiczną (linia czerwona),
  2. warstwę szczelności powietrznej / paroizolację (linia zielona) — po ciepłej stronie izolacji,
  3. hydroizolację / izolację przeciwwilgociową tam, gdzie jest wymagana (linia niebieska) — dachy, tarasy, podłogi na gruncie,
  4. warstwę wiatroizolacji / tynku zewnętrznego (ściany, spody stropów nad powietrzem zewnętrznym).
Podstawy: WT § 321, zał. 2 pkt 2.2.5 i 2.3.1 (szczelność), § 315–317 (izolacje przeciwwilgociowe i przeciwwodne),
§ 106 ust. 1 (szczelność garaż–dom na spaliny); zasady wiedzy technicznej (art. 5 PB).
Poziom przegród: sprawdzenie obecności i kolejności warstw. Ciągłość w węzłach (połączenia przegród) — lista par
przegród z węzłów modelu (`wezly`) z uwagami o łączeniu warstw; pełny audyt geometryczny „bez odrywania ołówka”
wykonują narzędzia rysunkowe (poza tym modułem).

Klasyfikacja funkcji warstwy — w kolejności: pole `funkcja` warstwy w przegrodzie → pole `funkcja` materiału →
kod kreskowania materiału (konwencja silnika, SCHEMAT_MODELU.md p. 5.4) → nazwa materiału (słowa kluczowe) → λ.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

FUNKCJE = ("izolacja", "paroizolacja", "szczelnosc", "hydroizolacja", "przeciwwilgociowa", "wiatroizolacja",
           "konstrukcja", "wykonczenie", "tynk", "pustka", "drenaz", "geowloknina", "bariera_korzenna", "substrat",
           "balast", "grunt", "spadkowa", "inna")

KRESK_FUNKCJA = {
    "IZOL_MIEKKA": "izolacja", "IZOL_TWARDA": "izolacja", "IZOL_XPS": "izolacja", "IZOL_PIR": "izolacja",
    "IZOLACJA_MIEKKA": "izolacja", "IZOLACJA_TWARDA": "izolacja",
    "IZOL_PRZECIWWODNA": "hydroizolacja", "IZOL_PRZECIWWILGOCIOWA": "przeciwwilgociowa",
    "PAROIZOLACJA": "paroizolacja", "MEMBRANA_PAROPRZEP": "wiatroizolacja",
    "ZELBET": "konstrukcja", "BETON": "konstrukcja", "BETON_LEKKI": "konstrukcja", "BETON_LEKKI_ZBROJONY": "konstrukcja",
    "BETON_KOMORKOWY": "konstrukcja", "MUR_CERAMIKA": "konstrukcja", "MUR_SILIKAT": "konstrukcja", "STAL": "konstrukcja",
    "DREWNO_POPRZ": "konstrukcja", "DREWNO_WZDL": "konstrukcja", "SKLEJKA": "wykonczenie",
    "PLYTA_DREWNOPOCHODNA": "wykonczenie", "TYNK": "tynk", "PLYTA_GK": "wykonczenie", "JASTRYCH": "wykonczenie",
    "PLYTKI": "wykonczenie", "DREWNO": "wykonczenie", "SZKLO": "wykonczenie",
    "GRUNT_RODZIMY": "grunt", "NASYP": "grunt", "PIASEK": "grunt", "ZWIR": "grunt", "POSPOLKA": "grunt",
    "HUMUS": "substrat", "GRUNT_NASYPOWY": "grunt",
}
# słowa kluczowe nazwy materiału (małe litery, bez polskich znaków diakrytycznych porównywane obie formy)
SLOWA = [
    (r"pustk|szczelin|powietrz|\bair\b|legar", "pustka"),
    (r"przeciwkorzen", "bariera_korzenna"),
    (r"geow[lł]*[oó]kn|w[lł]*[oó]knin|filtrac", "geowloknina"),
    (r"drena[zż]|kube[lł]k|mata drena", "drenaz"),
    (r"substrat|rozchodnik|sedum|ro[sś]linno", "substrat"),
    (r"[zż]wir|balast|otoczak", "balast"),
    (r"paroizol|folia pe|opó[zź]niacz pary|szczelno[sś]ci powietrz|folia paro", "paroizolacja"),
    (r"wiatroizol|paroprzepuszcz", "wiatroizolacja"),
    (r"przeciwwilgoc|dysperbit|folia fundament", "przeciwwilgociowa"),
    (r"hydroizol|\bpap[ay]\b|papa|epdm|\btpo\b|pvc-p|membran[ay] dach|przeciwwodn|kmb|bitumiczn[ay] grubowarstw|izolacja wodochronna",
     "hydroizolacja"),
    (r"spadk", "spadkowa"),
    (r"tynk", "tynk"),
    (r"styropian|\beps\b|\bxps\b|\bpir\b|\bpur\b|we[lł]na|izolacj[ai] termiczn|szk[lł]o piankowe|poliuretan|poliizocyjan|aerożel|aerozel",
     "izolacja"),
]

GRUNT_FUNKCJE = ("grunt",)
MEMBRANY = ("paroizolacja", "szczelnosc", "hydroizolacja", "przeciwwilgociowa", "wiatroizolacja", "bariera_korzenna",
            "geowloknina")


@dataclass
class MatProp:
    kod: str
    nazwa: str = ""
    lam: float | None = None
    rho: float | None = None
    cp: float | None = None
    mu: float | None = None
    sd: float | None = None          # jawny s_d [m] (np. membrany) — ma pierwszeństwo przed μ·d
    kreskowanie: str | None = None
    funkcja: str | None = None
    raw: dict = field(default_factory=dict)


def mat_props(materialy: Any, kod: str | None) -> MatProp:
    """Właściwości materiału z modelu (`Model.materialy` — słownik Material) albo ze słownika surowego."""
    if kod is None:
        return MatProp(kod="?")
    m = None
    if isinstance(materialy, dict):
        m = materialy.get(kod)
    if m is None:
        return MatProp(kod=kod, nazwa=kod)
    if isinstance(m, dict):
        raw = m
        lam = m.get("lambda")
    else:                                   # lamela.model.Material
        raw = m.raw or {}
        lam = m.lambda_
    return MatProp(kod=kod, nazwa=str(raw.get("nazwa", kod)), lam=_f(lam), rho=_f(raw.get("rho")), cp=_f(raw.get("cp")),
                   mu=_f(raw.get("mu")), sd=_f(raw.get("sd")), kreskowanie=raw.get("kreskowanie"),
                   funkcja=raw.get("funkcja"), raw=raw)


def _f(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def funkcja_warstwy(mp: MatProp, warstwa_raw: dict | None = None) -> str:
    """Funkcja warstwy (patrz nagłówek modułu)."""
    if warstwa_raw and warstwa_raw.get("funkcja"):
        return str(warstwa_raw["funkcja"])
    if warstwa_raw and warstwa_raw.get("pustka"):
        return "pustka"
    if mp.funkcja:
        return str(mp.funkcja)
    kod_nazwa = f"{mp.kod} {mp.nazwa}".lower()
    # nazwa ma pierwszeństwo przed kreskowaniem dla membran (kreskowanie „MEMBRANA” bywa wspólne)
    for wz, fn in SLOWA:
        if re.search(wz, kod_nazwa):
            if fn == "izolacja" and mp.lam is not None and mp.lam > 0.08:
                continue
            if fn == "spadkowa":
                return "izolacja" if (mp.lam is not None and mp.lam <= 0.065) else "spadkowa"
            return fn
    k = (mp.kreskowanie or "").upper()
    if k in KRESK_FUNKCJA:
        return KRESK_FUNKCJA[k]
    if mp.lam is not None and mp.lam <= 0.065:
        return "izolacja"
    return "inna"


def sd_warstwy(mp: MatProp, d: float) -> float:
    """Równoważna dyfuzyjnie grubość warstwy powietrza s_d = μ·d [m] (PN-EN ISO 13788:2013 p. 3.1.?)."""
    if mp.sd is not None:
        return mp.sd
    if mp.mu is None:
        return d * 1.0
    return mp.mu * d


# --------------------------------------------------------------------------------------------------
# Kontrola ciągłości warstw (poziom przegrody)
# --------------------------------------------------------------------------------------------------
@dataclass
class Uwaga:
    poziom: str          # BRAK | OSTRZEZENIE | INFO
    linia: str           # izolacja | szczelnosc | hydroizolacja | zewnetrzna | kolejnosc | inne
    opis: str


@dataclass
class WynikCiaglosci:
    kod: str
    nazwa: str
    rola: str
    warstwy: list[tuple[str, str, float]]      # (kod, funkcja, d)
    uwagi: list[Uwaga]
    elementy: list[str] = field(default_factory=list)   # elementy modelu używające przegrody w tej roli

    @property
    def braki(self) -> list[Uwaga]:
        return [u for u in self.uwagi if u.poziom == "BRAK"]

    @property
    def ok(self) -> bool:
        return not self.braki


ROLE_OPIS = {
    "sciana_zewn": "ściana zewnętrzna (do powietrza zewnętrznego)",
    "sciana_nieogrz": "ściana oddzielająca od pomieszczenia nieogrzewanego (garaż)",
    "dach": "stropodach / dach / taras nad pomieszczeniem ogrzewanym",
    "strop_zewn": "strop nad powietrzem zewnętrznym (spód wspornika)",
    "strop_nieogrz": "strop oddzielający od pomieszczenia nieogrzewanego",
    "podloga_grunt": "podłoga na gruncie / płyta fundamentowa",
}


def sprawdz_ciaglosc(kod: str, nazwa: str, warstwy: list[dict], materialy: Any, rola: str,
                     *, dach_odwrocony: bool | None = None, dach_zielony: bool | None = None) -> WynikCiaglosci:
    """Kontrola obecności i kolejności 4 „linii” w przegrodzie.

    `warstwy` — lista słowników {mat, d, [funkcja], [pustka], ...}; kolejność jak w modelu:
    ściany od wnętrza, przegrody poziome od góry. `rola` — klucz z ROLE_OPIS.
    """
    info = []
    for w in warstwy:
        mp = mat_props(materialy, w.get("mat"))
        fn = funkcja_warstwy(mp, w)
        info.append((mp, fn, float(w.get("d", 0.0)), w))
    fun = [f for _, f, _, _ in info]
    U: list[Uwaga] = []
    idx_iz = [i for i, f in enumerate(fun) if f in ("izolacja",)]
    idx_par = [i for i, f in enumerate(fun) if f in ("paroizolacja", "szczelnosc")]
    idx_hyd = [i for i, f in enumerate(fun) if f in ("hydroizolacja", "przeciwwilgociowa")]
    idx_tynk = [i for i, f in enumerate(fun) if f == "tynk"]
    idx_kon = [i for i, (mp, f, d, w) in enumerate(info) if f == "konstrukcja" or w.get("konstrukcyjna")]
    monolit = any((info[i][0].kreskowanie or "").upper() in ("ZELBET", "BETON") or
                  re.search(r"żelbet|zelbet|beton", info[i][0].nazwa.lower() or "") for i in idx_kon)

    # 1. izolacja termiczna
    if not idx_iz:
        U.append(Uwaga("BRAK", "izolacja", "brak warstwy izolacji termicznej"))
    ciepla_na_poczatku = rola != "dach"   # ściany: od wnętrza; podłogi/stropy: od góry (ciepło u góry); dach: ciepło u dołu
    iz0, iz1 = (min(idx_iz), max(idx_iz)) if idx_iz else (None, None)

    def po_cieplej(i):
        if iz0 is None:
            return True
        return i < iz0 if ciepla_na_poczatku else i > iz1

    def po_zimnej(i):
        if iz0 is None:
            return True
        return i > iz1 if ciepla_na_poczatku else i < iz0

    # 2. szczelność powietrzna / paroizolacja
    if rola in ("sciana_zewn", "sciana_nieogrz"):
        tynk_w = [i for i in idx_tynk if po_cieplej(i)]
        par_w = [i for i in idx_par if po_cieplej(i)]
        mono_w = [i for i in idx_kon if po_cieplej(i) and monolit]
        if not (tynk_w or par_w or mono_w):
            U.append(Uwaga("BRAK", "szczelnosc", "brak warstwy szczelności powietrznej po ciepłej stronie izolacji "
                           "(tynk wewnętrzny na murze, membrana paroizolacyjna lub monolityczny żelbet)"))
        elif tynk_w and not par_w:
            U.append(Uwaga("INFO", "szczelnosc", "szczelność powietrzną zapewnia tynk wewnętrzny — tynk ciągły do "
                           "stropu i posadzki, na ościeżach i za puszkami instalacyjnymi; taśmy przy oknach"))
        if rola == "sciana_nieogrz":
            if not (tynk_w or mono_w or par_w):
                U.append(Uwaga("BRAK", "szczelnosc", "przegroda garaż–dom bez warstwy szczelnej na spaliny (WT § 106 ust. 1)"))
    elif rola == "dach":
        odwr = dach_odwrocony
        if odwr is None:
            odwr = bool(idx_hyd and idx_iz and min(idx_hyd) > iz1)
        if odwr:
            U.append(Uwaga("INFO", "kolejnosc", "dach odwrócony — hydroizolacja pod izolacją pełni funkcję paroizolacji; "
                           "izolacja musi być nienasiąkliwa (XPS), poprawka ΔU_r wg PN-EN ISO 6946 zał. F"))
            iz_xps = all(re.search(r"xps|ekstrud", info[i][0].nazwa.lower() + info[i][0].kod.lower()) for i in idx_iz
                         if po_zimnej(min(idx_hyd)) or i < min(idx_hyd))
            if not iz_xps:
                U.append(Uwaga("OSTRZEZENIE", "izolacja", "dach odwrócony: izolacja nad hydroizolacją nie jest XPS"))
        else:
            par_w = [i for i in idx_par if po_cieplej(i)]
            if not par_w:
                U.append(Uwaga("BRAK", "szczelnosc", "brak paroizolacji pod izolacją termiczną stropodachu "
                               "(na płycie konstrukcyjnej — brief sekcja 9 pkt 5)"))
            hyd_z = [i for i in idx_hyd if po_zimnej(i)]
            if not hyd_z:
                U.append(Uwaga("BRAK", "hydroizolacja", "brak hydroizolacji (pokrycia) nad izolacją termiczną"))
        if dach_zielony is None:
            dach_zielony = "substrat" in fun
        if dach_zielony:
            for fn_req, opis in (("drenaz", "warstwy drenażowej"), ("geowloknina", "warstwy filtracyjnej (geowłóknina)")):
                if fn_req not in fun:
                    U.append(Uwaga("BRAK", "hydroizolacja", f"dach zielony: brak {opis}"))
            if "bariera_korzenna" not in fun and not any(
                    re.search(r"korzen", str(info[i][3].get("uwagi", "")) + info[i][0].nazwa.lower()) for i in idx_hyd):
                U.append(Uwaga("BRAK", "hydroizolacja", "dach zielony: brak bariery przeciwkorzennej (lub hydroizolacji "
                               "o deklarowanej odporności na przerastanie korzeni — PN-EN 13948)"))
    elif rola == "podloga_grunt":
        if not idx_hyd:
            U.append(Uwaga("BRAK", "hydroizolacja", "brak izolacji przeciwwilgociowej/przeciwwodnej podłogi na gruncie "
                           "(WT § 316 — ochrona przed wilgocią gruntową)"))
        par_w = [i for i in idx_par if po_cieplej(i)]
        if not par_w and not (monolit and any(po_cieplej(i) for i in idx_kon)) and not [i for i in idx_hyd if po_cieplej(i)]:
            U.append(Uwaga("OSTRZEZENIE", "szczelnosc", "brak warstwy paroizolacyjnej/rozdzielającej nad izolacją "
                           "(folia PE pod jastrychem) — szczelność zapewnia płyta żelbetowa pod izolacją?"))
        elif not par_w:
            U.append(Uwaga("INFO", "szczelnosc", "szczelność powietrzną zapewnia monolityczna płyta / izolacja przeciwwilgociowa"))
    elif rola == "strop_zewn":
        if not (monolit or idx_par):
            U.append(Uwaga("BRAK", "szczelnosc", "brak warstwy szczelności powietrznej (płyta monolityczna lub membrana)"))
    elif rola == "strop_nieogrz":
        if not (monolit or idx_par or idx_tynk):
            U.append(Uwaga("BRAK", "szczelnosc", "strop garaż–dom bez warstwy szczelnej na spaliny (WT § 106 ust. 1)"))

    # 3. hydroizolacja — tarasy/dachy obsłużone wyżej
    # 4. warstwa zewnętrzna (tynk/wiatroizolacja/okładzina) po zimnej stronie izolacji
    if rola in ("sciana_zewn", "strop_zewn") and idx_iz:
        zew = [i for i in range(len(fun)) if po_zimnej(i) and fun[i] in ("tynk", "wiatroizolacja", "wykonczenie", "inna",
                                                                           "konstrukcja")]
        if not zew:
            U.append(Uwaga("BRAK", "zewnetrzna", "brak warstwy zewnętrznej (tynk / wiatroizolacja / okładzina) na izolacji"))
        else:
            wm = [i for i in idx_iz if re.search(r"we[lł]n|mineral", info[i][0].nazwa.lower())]
            pustka_zew = [i for i in range(len(fun)) if po_zimnej(i) and fun[i] == "pustka"]
            if wm and pustka_zew and not any(fun[i] == "wiatroizolacja" for i in range(len(fun)) if po_zimnej(i)):
                U.append(Uwaga("BRAK", "zewnetrzna", "fasada wentylowana na wełnie mineralnej bez wiatroizolacji"))
    # paroizolacja po zimnej stronie (błąd kolejności) — ściany/stropy
    if rola != "dach":
        for i in idx_par:
            if po_zimnej(i) and fun[i] == "paroizolacja":
                U.append(Uwaga("OSTRZEZENIE", "kolejnosc", f"paroizolacja '{info[i][0].kod}' po zimnej stronie izolacji "
                               "— ryzyko kondensacji (sprawdzić Glaserem)"))
    return WynikCiaglosci(kod=kod, nazwa=nazwa, rola=rola,
                          warstwy=[(mp.kod, fn, d) for mp, fn, d, _ in info], uwagi=U)


def uwagi_wezla(wezel: dict, przegrody: dict, materialy: Any, role: dict[str, str]) -> list[Uwaga]:
    """Uwagi o łączeniu linii w węźle (para przegród z `wezly[].przegrody`). `role` — kod przegrody → rola."""
    out = []
    kody = [str(k) for k in (wezel.get("przegrody") or [])]
    typy = {}
    for k in kody:
        p = przegrody.get(k)
        if p is None:
            out.append(Uwaga("BRAK", "inne", f"węzeł {wezel.get('id')}: przegroda '{k}' nie istnieje w modelu"))
            continue
        ws = [{"mat": w.mat, "d": w.d} for w in p.warstwy] if hasattr(p, "warstwy") else p.get("warstwy", [])
        fun = [funkcja_warstwy(mat_props(materialy, w["mat"]), w) for w in ws]
        typy[k] = fun
        if "izolacja" not in fun and role.get(k) not in (None, "wewn"):
            out.append(Uwaga("BRAK", "izolacja", f"węzeł {wezel.get('id')}: przegroda {k} bez izolacji — przerwana linia izolacji"))
    if len(typy) >= 2:
        sz = {k: ("paroizolacja" in f or "szczelnosc" in f, "tynk" in f) for k, f in typy.items()}
        rodz = {("membrana" if a else ("tynk" if b else "brak")) for a, b in sz.values()}
        if len(rodz) > 1:
            out.append(Uwaga("INFO", "szczelnosc", f"węzeł {wezel.get('id')}: różne warstwy szczelności ({', '.join(sorted(rodz))}) "
                             "— połączenie taśmą/klejem systemowym, wyprowadzenie paroizolacji na ścianę ≥ 10 cm"))
    return out
