"""Katalog przyborów sanitarnych i punktów czerpalnych oraz odczyt ich rozmieszczenia z modelu.

Dla każdego typu przyboru (klucze = ``typ`` w ``model/wyposazenie.yaml``, rozszerzone o typy wyłącznie instalacyjne):

* **q_n** — normatywny wypływ wody zimnej / ciepłej [dm³/s] i wymagane ciśnienie wypływu p_w [kPa]
  wg PN-92/B-01706 tabl. 1 (norma wycofana, wiążąca przez WT §113 ust. 4 i zał. 1 lp. 4) — wartości wg materiałów
  PWr „Materiały pomocnicze do projektu instalacji wodociągowej” (R6-50) [W];
* **LU** — jednostki obciążenia wg PN-EN 806-3:2006 tabl. 2 (1 LU ≙ Q_A = 0,1 l/s) — kontrolnie (R6-51) [W];
* **DU** — równoważnik odpływu [l/s], system I wg PN-EN 12056-2:2002 tabl. 2 (R6-57) [NZW];
* **DN podejścia** kanalizacyjnego (praktyka projektowa; R6 §3.7 [NZW]) i minimalna średnica podejścia wody.

Rozmieszczenie: ``wyposazenie.yaml`` (typy sanitarne: wc, umywalka, umywalka_blat, wanna, prysznic, pralka, suszarka,
zlew, zmywarka) + ``instalacje.yaml: przybory_dodatkowe`` (np. bidet, zawor_ogrodowy, wpust_podlogowy, zlewik,
zawor_czerpalny, pisuar) — punkt ``xy`` leży na licu ściany (jak w wyposażeniu), przypisanie do pomieszczenia
przez odsunięcie 0,30 m w kierunku ``obrot``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import DaneBudynku


@dataclass(frozen=True)
class TypPrzyboru:
    nazwa: str
    qn_zw: float          # dm³/s
    qn_cw: float          # dm³/s
    p_w: float            # kPa — wymagane ciśnienie wypływu
    LU_zw: float
    LU_cw: float
    DU: float             # l/s (PN-EN 12056-2, system I)
    dn_kan: int | None    # DN podejścia kanalizacyjnego (None — bez odpływu do kanalizacji)
    dz_wod: int = 16      # min. średnica zewn. podejścia wody (rura wielowarstwowa) [mm]
    cwu: bool = False     # czy zasilany c.w.u.
    kat_1717: int = 2     # kategoria płynu wg PN-EN 1717 na wypływie (2 — woda zmieniona temperaturowo)
    uwagi: str = ""


# Źródła: PN-92/B-01706 tabl. 1 (PWr); PN-EN 806-3 tabl. 2; PN-EN 12056-2 tabl. 2 — zob. docstring
KATALOG: dict[str, TypPrzyboru] = {
    "wc": TypPrzyboru("Miska ustępowa z płuczką zbiornikową 6 l", 0.13, 0.0, 50, 1, 0, 2.0, 100, 16,
                      uwagi="p_w = 50 kPa (płuczka); podejście kan. DN100 (110)"),
    "umywalka": TypPrzyboru("Umywalka z baterią", 0.07, 0.07, 100, 1, 1, 0.5, 40, 16, True),
    "umywalka_blat": TypPrzyboru("Umywalka nablatowa z baterią", 0.07, 0.07, 100, 1, 1, 0.5, 40, 16, True),
    "bidet": TypPrzyboru("Bidet z baterią", 0.07, 0.07, 100, 1, 1, 0.5, 40, 16, True),
    "wanna": TypPrzyboru("Wanna z baterią", 0.15, 0.15, 100, 4, 4, 0.8, 50, 16, True),
    "prysznic": TypPrzyboru("Natrysk (odpływ liniowy/brodzik bez korka) z baterią", 0.15, 0.15, 100, 2, 2, 0.6, 50, 16, True,
                            uwagi="q_n natrysku rozbieżne w źródłach (0,07–0,15) — przyjęto 0,15 (R6 Nierozstrz. 6)"),
    "zlew": TypPrzyboru("Zlewozmywak z baterią", 0.07, 0.07, 100, 2, 2, 0.8, 50, 16, True),
    "zlewik": TypPrzyboru("Zlew gospodarczy z baterią", 0.07, 0.07, 100, 2, 2, 0.8, 50, 16, True),
    "zmywarka": TypPrzyboru("Zmywarka do naczyń", 0.15, 0.0, 100, 2, 0, 0.8, 50, 16,
                            uwagi="odpływ do syfonu zlewozmywaka (DU liczony osobno)"),
    "pralka": TypPrzyboru("Pralka automatyczna (≤ 12 kg)", 0.25, 0.0, 100, 2, 0, 1.5, 50, 16,
                          uwagi="DU 1,5 (pralka ≤ 12 kg); ≤ 6 kg: 0,8"),
    "suszarka": TypPrzyboru("Suszarka kondensacyjna z odprowadzeniem skroplin", 0.0, 0.0, 0, 0, 0, 0.0, 40, 16,
                            uwagi="skropliny do syfonu pralki — pomijalny DU"),
    "zawor_ogrodowy": TypPrzyboru("Zawór czerpalny ogrodowy DN15 ze złączką do węża", 0.30, 0.0, 100, 5, 0, 0.0, None, 20,
                                  kat_1717=3, uwagi="zabezpieczenie HA/HD (PN-EN 1717, kat. 3 — wąż)"),
    "zawor_czerpalny": TypPrzyboru("Zawór czerpalny DN15 z perlatorem (garaż/pom. techn.)", 0.15, 0.0, 100, 2, 0, 0.0, None, 16),
    "wpust_podlogowy": TypPrzyboru("Wpust podłogowy DN50", 0.0, 0.0, 0, 0, 0, 0.8, 50, 16),
    "wpust_podlogowy_100": TypPrzyboru("Wpust podłogowy DN100", 0.0, 0.0, 0, 0, 0, 2.0, 100, 16),
    "pisuar": TypPrzyboru("Pisuar z zaworem spłukującym", 0.30, 0.0, 100, 1, 0, 0.5, 50, 16),
}
TYPY_SANITARNE = set(KATALOG)
ALIASY = {"natrysk": "prysznic", "brodzik": "prysznic", "miska": "wc", "zlewozmywak": "zlew", "umywalka_nablatowa": "umywalka_blat"}


@dataclass
class Przybor:
    id: str
    typ: str
    kond: str
    xy: tuple
    pom: str | None
    pom_nazwa: str
    z: float                        # rzędna posadzki [m]
    h_wyl: float = 1.0              # wysokość wypływu nad posadzką [m]
    zrodlo: str = "wyposazenie"

    @property
    def t(self) -> TypPrzyboru:
        return KATALOG[self.typ]

    @property
    def z_wyl(self) -> float:
        return self.z + self.h_wyl


H_WYLOTU = {"wc": 0.80, "umywalka": 1.10, "umywalka_blat": 1.20, "bidet": 0.40, "wanna": 0.75, "prysznic": 1.20,
            "zlew": 1.15, "zlewik": 1.10, "zmywarka": 0.60, "pralka": 0.80, "zawor_ogrodowy": 0.60,
            "zawor_czerpalny": 1.00, "pisuar": 1.20}  # PWr: wysokości armatury nad posadzką [W]


def przybory_z_modelu(dane: DaneBudynku) -> list[Przybor]:
    """Lista przyborów z ``wyposazenie.yaml`` + ``instalacje.yaml: przybory_dodatkowe`` (typy z :data:`KATALOG`)."""
    out: list[Przybor] = []
    zrodla = [(e, "wyposazenie") for e in dane.wyposazenie] + \
             [(e, "instalacje") for e in (dane.inst.get("przybory_dodatkowe") or [])]
    n = 0
    for e, src in zrodla:
        typ = ALIASY.get(str(e.get("typ", "")), str(e.get("typ", "")))
        if typ not in KATALOG or not e.get("xy"):
            continue
        kond = str(e.get("kond", "P0"))
        x, y = float(e["xy"][0]), float(e["xy"][1])
        a = math.radians(float(e.get("obrot", 90.0)))
        probe = (x + 0.30 * math.cos(a), y + 0.30 * math.sin(a))
        r = dane.pom_w_punkcie(kond, probe, tol=0.35) or dane.pom_w_punkcie(kond, (x, y), tol=0.5)
        n += 1
        if typ == "zawor_ogrodowy":
            r = None
        out.append(Przybor(id=f"{typ.upper()[:3]}{n:02d}", typ=typ, kond=kond, xy=(x, y),
                           pom=(r.id if r else None), pom_nazwa=(r.nazwa if r else "na zewnątrz / poza pomieszczeniem"),
                           z=dane.rzedna(kond), h_wyl=H_WYLOTU.get(typ, 1.0), zrodlo=src))
    return out


def zestawienie(przybory: list[Przybor]) -> list[list]:
    """Wiersze tabeli: typ, liczba, q_n zw/cw, LU, DU (sumy)."""
    agg: dict[str, int] = {}
    for p in przybory:
        agg[p.typ] = agg.get(p.typ, 0) + 1
    rows = []
    for typ, n in sorted(agg.items()):
        t = KATALOG[typ]
        rows.append([t.nazwa, n, t.qn_zw, t.qn_cw, n * (t.qn_zw + t.qn_cw), t.LU_zw + t.LU_cw, t.DU,
                     f"DN{t.dn_kan}" if t.dn_kan else "—"])
    return rows


# ==================================================================================================
# Piony (grupowanie pomieszczeń mokrych w pionie)
# ==================================================================================================
@dataclass
class Pion:
    id: str
    xy: tuple
    kondygnacje: list                   # kondygnacje z podłączeniami (rosnąco)
    pomieszczenia: dict = field(default_factory=dict)   # kond → [id pomieszczeń]
    przybory: list = field(default_factory=list)        # [Przybor]
    zrodlo: str = "auto"

    @property
    def ma_wc(self) -> bool:
        return any(p.typ == "wc" for p in self.przybory)


R_PIONU = 3.5   # m — maks. odległość w rzucie pomieszczenia mokrego od pionu [UPR]


def grupy_pionow(dane: DaneBudynku, przybory: list[Przybor]) -> list[Pion]:
    """Grupuje przybory w piony: jawne ``instalacje.piony`` ([{id, xy}]) albo automatycznie — pomieszczenia mokre
    kolejnych kondygnacji leżące w rzucie ≤ R_PIONU od pionu (pion w osi miski ustępowej lub w środku przyborów
    najniższego pomieszczenia) [UPR]. Przybory poza pomieszczeniami (zawory ogrodowe) nie tworzą pionów."""
    kond_idx = {k["id"]: i for i, k in enumerate(dane.kondygnacje)}
    wew = [p for p in przybory if p.pom is not None]
    by_room: dict[tuple, list[Przybor]] = {}
    for p in wew:
        by_room.setdefault((p.kond, p.pom), []).append(p)
    # tylko piony kanalizacyjne: pole `rodzaj` (instalacje.piony, runda 2 K-8) — rury spustowe, piony c.o., wentylacji
    # i teletechniki nie zbierają przyborów (brak pola → zgodność wstecz: kanalizacja)
    jawne = [j for j in (dane.inst.get("piony") or []) if str(j.get("rodzaj") or "kanalizacja") == "kanalizacja"]
    piony: list[Pion] = [Pion(id=str(j.get("id", f"P{i + 1}")), xy=(float(j["xy"][0]), float(j["xy"][1])),
                              kondygnacje=[], zrodlo="instalacje.yaml") for i, j in enumerate(jawne) if j.get("xy")]
    rooms = sorted(by_room.items(), key=lambda kv: (kond_idx.get(kv[0][0], 0), kv[0][1]))
    for (kond, pid), lst in rooms:
        wc = [p for p in lst if p.typ == "wc"]
        ref = wc[0].xy if wc else (sum(p.xy[0] for p in lst) / len(lst), sum(p.xy[1] for p in lst) / len(lst))
        cx = sum(p.xy[0] for p in lst) / len(lst)
        cy = sum(p.xy[1] for p in lst) / len(lst)
        best, dbest = None, 1e9
        for pn in piony:
            d = math.hypot(pn.xy[0] - cx, pn.xy[1] - cy)
            if d < dbest:
                best, dbest = pn, d
        if best is None or (dbest > R_PIONU and best.zrodlo == "auto") or (dbest > 2 * R_PIONU):
            best = Pion(id=f"P{len(piony) + 1}", xy=(round(ref[0], 2), round(ref[1], 2)), kondygnacje=[])
            piony.append(best)
        best.pomieszczenia.setdefault(kond, []).append(pid)
        best.przybory += lst
        if kond not in best.kondygnacje:
            best.kondygnacje.append(kond)
    for pn in piony:
        pn.kondygnacje.sort(key=lambda k: kond_idx.get(k, 0))
        # pion z WC — przesunięcie osi do miski ustępowej najniższej kondygnacji (jeśli pion automatyczny)
        if pn.zrodlo == "auto":
            wcs = [p for p in pn.przybory if p.typ == "wc"]
            if wcs:
                w0 = min(wcs, key=lambda p: kond_idx.get(p.kond, 0))
                pn.xy = (round(w0.xy[0], 2), round(w0.xy[1], 2))
    return [p for p in piony if p.przybory]
