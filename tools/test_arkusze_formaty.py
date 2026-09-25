#!/usr/bin/env python3
"""Testy silnika ekonomicznego ustawienia na arkuszach (``lamela.views.uklad``, ``lamela.draft.skladanie``).

Sprawdza: pasy składania do A4 (harmonijka: pasy ≤ 210 mm, w parach równych, pas z tabliczką ≥ 190 mm na
wierzchu, pasy „ładne” 180–210 mm), plan składania (``plan_skladania``), formaty niestandardowe arkusza, podział
uwag, brak nakładania bloków i widoków, zgodność wsteczną (formaty jawne, tryb klasyczny, kontrakt
``register_view``: column_blocks, units_note, bez_skali, qa) i determinizm; poprawki zgłoszone przez zespoły
zastosowania (docs/30_arkusze/zastosowanie_*.md): strefy i przycinanie znaków centrujących, kolejność czytania
części uwag i kolumn bloków, kara za rozdrobnienie uwag, wyśrodkowanie bez pogorszenia, dziedziczenie ``nr`` i
scalanie bloków widoków, łamanie tekstu w tabelach (zestawienie pomieszczeń, spis tomu), zamiennik glifu ⌀,
odcinek kontrolny a znak centrujący.

Uruchomienie:
    PYTHONPATH=src python3 tools/test_arkusze_formaty.py [--szybko]    # --szybko: bez arkuszy z modelu testowego
Funkcje test_* są zgodne z pytest.
"""
from __future__ import annotations

import random
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.draft import skladanie as SK  # noqa: E402
from lamela.draft.sheet import Sheet, fold_positions, notes_box, sheet_size  # noqa: E402
from lamela.views import uklad as U  # noqa: E402

B_TEST = ROOT / "model" / "test" / "dom_testowy.yaml"
D_TEST = ROOT / "model" / "test" / "dzialka_testowa.yaml"


# ================================================================================================ składanie
def _paczka(pasy):
    """Symulacja harmonijki: pierwszy pas licem do góry na [0, w1]; zwraca (zakresy pasów w paczce, x prawej
    krawędzi arkusza w paczce)."""
    x = pasy[0]
    zakresy = [(0.0, pasy[0])]
    znak = -1.0
    for w in pasy[1:]:
        x2 = x + znak * w
        zakresy.append((min(x, x2), max(x, x2)))
        x = x2
        znak = -znak
    return zakresy, x


def test_pasy_skladania():
    for W in [float(w) for w in range(211, 2600, 3)] + [297.0, 420.0, 594.0, 841.0, 891.0, 1189.0, 1261.0]:
        pasy = SK.pasy_pionowe(W)
        assert abs(sum(pasy) - W) < 1e-6, (W, pasy)
        assert len(pasy) % 2 == 1, f"{W}: parzysta liczba pasów {pasy} — tabliczka nie trafi na wierzch"
        assert pasy[-1] >= 190.0 - 1e-6, f"{W}: pas z tabliczką {pasy[-1]} < 190"
        assert all(p <= 210.0 + 1e-6 for p in pasy), f"{W}: pas > 210 mm {pasy}"
        assert all(p > 0 for p in pasy), (W, pasy)
        zakresy, xr = _paczka(pasy)
        assert abs(xr - 210.0) < 1e-6, f"{W}: prawa krawędź arkusza w paczce {xr} ≠ 210 (tabliczka nie w rogu)"
        assert all(a >= -1e-6 and b <= 210.0 + 1e-6 for a, b in zakresy), f"{W}: pas poza paczką A4 {zakresy}"
        if pasy[0] < 210.0 - 1e-6:                       # rodzina B: pasy 2…N nie zasłaniają marginesu na oprawę
            assert all(a >= 20.0 - 1e-6 for a, _b in zakresy[1:]), (W, zakresy)
        else:                                            # rodzina A: pary równe (warunek zamknięcia harmonijki)
            mid = pasy[1:]
            for i in range(0, len(mid), 2):
                assert abs(mid[i] - mid[i + 1]) < 1e-6, (W, pasy)
        oc0 = SK.ocena_pionowa(pasy, W)[0]
        for c in SK.warianty_pasow(W):                   # wybrany wariant ma najlepszą ocenę spośród poprawnych
            assert SK.RANK[SK.ocena_pionowa(c, W)[0]] <= SK.RANK[oc0], (W, c, pasy)
        oc = SK.ocena_skladania(W, 420.0)
        if oc["ocena_pion"] == "dobre" and W > 420.5:
            assert all(180.0 - 1e-6 <= p <= 210.0 + 1e-6 for p in pasy[1:-1]), (W, pasy)
    # poziomo: co 297 mm od dołu
    for H, rz in ((297, [297]), (420, [297, 123]), (594, [297, 297]), (841, [297, 297, 247]), (891, [297] * 3)):
        assert [round(r) for r in SK.rzedy_poziome(H)] == rz, (H, SK.rzedy_poziome(H))


def test_skladanie_formaty_standardowe():
    """Formaty, dla których dawny algorytm dawał pasy równe — bez zmian; A3: margines na krawędzi paczki."""
    assert fold_positions(594, 420) == ([210.0, 402.0], [297.0])
    assert fold_positions(891, 420)[0] == [210.0, 360.5, 511.0, 701.0]
    assert fold_positions(841, 594) == ([210.0, 335.5, 461.0, 651.0], [297.0])
    assert fold_positions(420, 297) == ([125.0, 230.0], [])            # 125 + 105 + 190 (DIN 824 A)
    assert fold_positions(210, 297) == ([], [])
    assert fold_positions(970, 297)[0] == [210.0, 400.0, 590.0, 780.0]
    for L in (590, 970, 1350, 1730):                                     # L = 210 + 190·n, n parzyste
        assert SK.ocena_skladania(L, 594)["ocena"] == "dobre", L
    # n nieparzyste: rodzina A dałaby parę 95 mm (210 + 95 + 95 + 190 + 190); rodzina B — pasy 142,5 mm
    assert SK.pasy_pionowe(780) == [162.5, 142.5, 142.5, 142.5, 190.0]
    assert SK.ocena_skladania(780, 297)["ocena_pion"] == "poprawne"
    assert SK.pasy_pionowe(690) == [140.0, 120.0, 120.0, 120.0, 190.0]
    assert min(SK.pasy_pionowe(650)) >= 110.0 - 1e-6
    for W, H in ((630.0000037, 594.0000047), (629.9999962, 593.9999951), (419.9999881, 594.0000047)):
        assert SK.ocena_skladania(W, H)["pasy"] == SK.ocena_skladania(round(W), round(H))["pasy"], (W, H)  # z PDF


def test_plan_skladania():
    from lamela.dokumenty.arkusze import Arkusz, plan_skladania
    pl = plan_skladania([Arkusz(nr="A", format="A3x3"), Arkusz(nr="B", format="970×594"),
                         Arkusz(nr="C", format="nst. 630×297"), Arkusz(nr="D", format="A4")])
    d = {p["nr"]: p for p in pl}
    assert d["A"]["wymiary"] == "891×420" and d["A"]["pasy"][-1] == 190.0
    assert d["B"]["ocena"] == "dobre" and d["B"]["zlozenia_poziome"] == [297.0]
    assert d["C"]["pasy"] == [210.0, 210.0, 210.0] and d["C"]["tabliczka_na_wierzchu"]
    assert d["D"]["opis"] == "bez składania (A4)"
    for p in pl:
        assert p["tabliczka_na_wierzchu"], p


def test_arkusz_niestandardowy():
    assert sheet_size("780x594") == (780.0, 594.0)
    assert sheet_size("594×780") == (594.0, 780.0)
    assert sheet_size("A3x3") == (891, 420) and sheet_size("A2") == (594, 420) and sheet_size("A4") == (210, 297)
    sh = Sheet("780x594")
    assert (sh.width, sh.height) == (780.0, 594.0) and sh.fmt_name == "780×594" and sh.custom
    xs, ys = fold_positions(780, 594)
    ticks = [p for p in sh.prims if getattr(p, "pts", None) is not None and len(p.pts) == 2
             and abs(p.pts[0][1]) < 1e-9 and abs(p.pts[1][1] - 5.0) < 1e-9]
    assert sorted(round(float(p.pts[0][0]), 1) for p in ticks) == [round(x, 1) for x in xs]
    labels = [p.string for p in sh.prims if hasattr(p, "runs") and p.pos[1] < 3.0 and not p.string.startswith("nst.")]
    assert sorted(labels) == [str(i + 1) for i in range(len(xs))], labels
    txt = [p.string for p in sh.prims if hasattr(p, "runs")]
    assert "nst. 780×594" in txt
    assert not Sheet("A3x3").custom and Sheet("A3x3").fmt_name == "A3×3"


# ================================================================================================ upakowanie
def _blok_prosty(h, w=U.B_W):
    def fn(sh, x, y, ww):
        sh.rect(x, y - h, x + ww, y)
        sh.text((x + 2, y - 5), "BLOK", 2.5)
        return y - h
    return U.blok(f"blok{h:.0f}", fn, w)


def _uwagi(n=12):
    b = U.Blok("uwagi", None, U.B_W)
    b.uwagi = U.BlokUwag([f"Uwaga numer {i + 1}: " + "tekst uwagi do zawinięcia w kolumnie " * (1 + i % 4)
                          for i in range(n)])
    return b


def _przypadki(seed=7, n=40):
    rnd = random.Random(seed)
    out = [([(600, 330)], [110, 40, 30]), ([(680, 210)], [60, 14]), ([(150, 100)], [30]),
           ([(300, 200), (250, 180), (200, 150)], [60, 80]), ([(900, 560)], [300, 200, 120]),
           ([(120, 90)] * 7, [40, 40, 40])]
    for _ in range(n):
        nv = rnd.randint(1, 4)
        out.append(([(rnd.uniform(60, 700), rnd.uniform(50, 420)) for _ in range(nv)],
                    [rnd.uniform(10, 160) for _ in range(rnd.randint(0, 5))]))
    return out


def _sprawdz_uklad(u, widoki, tb_h):
    R = u.roz
    assert R.ok, R.brak
    bl = U.sprawdz_nakladanie(R)
    assert not bl, bl
    tb = R.tabliczka
    fx0, fy0, fx1, fy1 = U.rama(u.W, u.H)
    assert abs(tb[2] - fx1) < 1e-6 and abs(tb[1] - fy0) < 1e-6, "tabliczka poza prawym dolnym rogiem"
    rects = [(k, n, r) for k, n, r in R.prostokaty if k != "znak"]   # strefy znaków: sprawdz_nakladanie
    for i, (k1, n1, a) in enumerate(rects):              # minimalne odstępy
        for k2, n2, b in rects[i + 1:]:
            if n1 == n2 and {k1, k2} <= {"widok", "tytul"}:
                continue
            dx = max(b[0] - a[2], a[0] - b[2])
            dy = max(b[1] - a[3], a[1] - b[3])
            gap = max(dx, dy)
            kw = {"tytul": "widok"}
            k1w, k2w = kw.get(k1, k1), kw.get(k2, k2)
            need = U.GAP_VB if "widok" in (k1w, k2w) else min(U.GAP_B, U.GAP_C)
            if {k1w, k2w} == {"widok"}:
                need = min(need, U.GAP_V)
            assert gap >= need - 0.05, f"odstęp {gap:.1f} < {need} mm: {k1} {n1} ↔ {k2} {n2}"
    ok = SK.ocena_skladania(u.W, u.H, tb_h)
    assert ok["tabliczka_na_wierzchu"], (u.nazwa, ok)
    assert tb[0] >= u.W - ok["pasy"][-1] - 1e-6 and tb[3] <= ok["rzedy"][0] + 1e-6, "tabliczka poza pasem wierzchnim"


def _sprawdz_czesci_uwag(R, n):
    """Części uwag: numeracja ciągła 1…n, kolejność czytania (część k+1 pod k w kolumnie albo w kolumnie na
    prawo), ≥ 2 pozycje w części (gdy n ≥ 2 i jest więcej niż jedna część)."""
    import re
    parts = [(b.nazwa, r) for (b, *_x), (k, nm, r) in zip(R.bloki, [p for p in R.prostokaty if p[0] == "blok"])
             if b.nazwa.startswith("uwagi[")]
    zakresy = [tuple(int(v) for v in re.findall(r"\d+", nm)) for nm, _r in parts]
    assert zakresy[0][0] == 1 and zakresy[-1][1] == n, zakresy
    for (a0, a1), (b0, b1) in zip(zakresy, zakresy[1:]):
        assert b0 == a1 + 1, zakresy
    for (_n1, r1), (_n2, r2) in zip(parts, parts[1:]):
        assert U._po(r1, r2), f"część „{_n2}” {r2} przed „{_n1}” {r1} w kolejności czytania"
    if len(parts) > 1:
        assert all(a1 - a0 + 1 >= 2 for a0, a1 in zakresy), zakresy


def test_brak_nakladania():
    for views, blocks in _przypadki():
        widoki = [U.Widok(f"v{i}", w, h, min(w, 140.0), 10.5) for i, (w, h) in enumerate(views)]
        bloki = [_blok_prosty(h) for h in blocks] + [_uwagi(8)]
        u = U.rozmiesc(widoki, bloki, 103.0, {})
        if u is None:
            continue
        _sprawdz_uklad(u, widoki, 103.0)
        assert u.W <= 2400 + 1e-6 and u.H <= 914 + 1e-6


def test_kieszenie_widoku():
    """Blok w pustym narożniku obwiedni widoku (kształt L) — bez kolizji z zajętością widoku."""
    v = U.Widok("L", 500, 300, 120, 10.5, False, [(0, 0, 500, 150), (0, 150, 250, 300)])
    u = U.rozmiesc([v], [_blok_prosty(100), _blok_prosty(40)], 103.0, {})
    _sprawdz_uklad(u, [v], 103.0)
    uz = U.rozmiesc([U.Widok("P", 500, 300, 120, 10.5)], [_blok_prosty(100), _blok_prosty(40)], 103.0, {})
    assert u.W * u.H <= uz.W * uz.H + 1e-6


def test_uwagi_dzielone():
    U_ = U.BlokUwag([f"Uwaga {i}: " + "długi tekst uwagi " * (i % 5 + 1) for i in range(9)])
    for i0, i1 in ((0, 9), (0, 4), (4, 9), (3, 5)):
        sh = Sheet("A0", draw_frame=False)
        r = notes_box(sh, 50.0, 700.0, U.B_W, U_.lines[i0:i1], "T", h=1.8, start=i0 + 1)
        assert abs((700.0 - r[1]) - U_.wysokosc(i0, i1)) < 0.05, (i0, i1, 700 - r[1], U_.wysokosc(i0, i1))
        nums = [p.string for p in sh.prims if hasattr(p, "runs") and p.string.rstrip().endswith(".")
                and p.string.strip()[:-1].isdigit()]
        assert nums[0].strip() == f"{i0 + 1}.", nums
    # wysoka kolumna uwag na niskim arkuszu → podział na części z ciągłą numeracją (w kolejności czytania)
    u = U.rozmiesc([U.Widok("v", 700, 240, 100, 10.5)], [_uwagi(70)], 103.0,
                   {"wysokosci": [297], "max_wysokosc": 297, "max_czesci_uwag": 8}, fmt="ekonomiczny")
    czesci = [(b, x, y) for b, x, y, _w in u.roz.bloki if b.nazwa.startswith("uwagi[")]
    assert len(czesci) >= 2, [b.nazwa for b, *_ in u.roz.bloki]
    _sprawdz_uklad(u, [], 103.0)
    _sprawdz_czesci_uwag(u.roz, 70)


def test_bloki_zalezne_od_arkusza():
    """Bloki ze stanem arkusza (jak w detalach: legenda raz na arkusz, wyniki z nagłówkiem tylko przy pierwszym) —
    powtórzenia pomijane, ciągi dalsze łączone z poprzednim blokiem (jak w kolumnie klasycznej)."""
    def legenda(sh, x, y, w):
        if getattr(sh, "_t_leg", False):
            return y
        sh._t_leg = True
        sh.rect(x, y - 30, x + w, y)
        return y - 30

    def wyniki(i):
        def fn(sh, x, y, w):
            if not getattr(sh, "_t_wyn", False):
                sh._t_wyn = True
                sh.text((x, y - 3.5), "WYNIKI", 3.5)
                y -= 8.0
            sh.text((x, y - 2), f"wynik {i}", 1.8)
            return y - 6.0
        return fn
    pary = [("leg", legenda), ("wyn-1", wyniki(1)), ("leg", legenda), ("wyn-2", wyniki(2)), ("leg", legenda),
            ("wyn-3", wyniki(3)), ("tab", lambda sh, x, y, w: (sh.rect(x, y - 20, x + w, y), y - 20)[1])]
    bl = U.bloki_z_kolumny(pary)
    assert [b.nazwa for b in bl] == ["leg", "wyn-1 + wyn-2 + wyn-3", "tab"], [b.nazwa for b in bl]
    sh = Sheet("A0", draw_frame=False)
    yb = bl[1].fn(sh, 10.0, 500.0, U.TB_W)
    assert abs((500.0 - yb) - bl[1].h) < 0.5
    txt = [p.string for p in sh.prims if hasattr(p, "runs")]
    assert txt.count("WYNIKI") == 1 and {"wynik 1", "wynik 2", "wynik 3"} <= set(txt)


def test_tryby_i_opcje():
    assert U.tryb_formatu("auto")[0] == "ekonomiczny" and U.tryb_formatu(None)[0] == "ekonomiczny"
    assert U.tryb_formatu("klasyczny")[0] == "klasyczny" and U.tryb_formatu("standardowy")[0] == "standardowy"
    assert U.tryb_formatu([594, 780]) == ("jawny", ("780×594", 780.0, 594.0))
    assert U.tryb_formatu("780x594")[1][1:] == (780.0, 594.0)
    assert U.tryb_formatu("A3x3")[1][1:] == (891, 420)
    o = U.opcje({"kara_niestandard": 0.05, "kara_skladania": {"słabe": 0.2}}, {"wysokosci": [594]})
    assert o["kara_niestandard"] == 0.05 and o["wysokosci"] == [594]
    assert o["kara_skladania"]["słabe"] == 0.2 and o["kara_skladania"]["poprawne"] == 0.04
    assert U.dlugosci_kandydaci(700, dict(o, modul_skladania=190)) == [780.0, 970.0, 1160.0]
    assert U.dlugosci_kandydaci(700, dict(o, modul_skladania=0)) == [700.0]
    assert U.nazwa_standardowa(594, 420) == ("A2", "landscape") and U.nazwa_standardowa(420, 594)[1] == "portrait"
    assert U.nazwa_standardowa(780, 594) is None


def test_format_jawny_i_standardowy():
    v = [U.Widok("v", 600, 330, 150, 10.5)]
    b = [_blok_prosty(110), _blok_prosty(40)]
    u = U.rozmiesc(v, b, 103.0, {}, fmt="A1")
    assert (u.nazwa, u.W, u.H, u.standard) == ("A1", 841, 594, True)
    _sprawdz_uklad(u, v, 103.0)
    u = U.rozmiesc(v, b, 103.0, {}, fmt=[594, 780])
    assert (u.W, u.H, u.standard) == (780.0, 594.0, False)
    assert U.rozmiesc(v, b, 103.0, {}, fmt="A3") is None          # nie mieści się → sheets.py: układ klasyczny
    u = U.rozmiesc(v, b, 103.0, {}, fmt="standardowy")
    assert u.standard and U.nazwa_standardowa(u.W, u.H) is not None
    ue = U.rozmiesc(v, b, 103.0, {})
    assert ue.koszt <= u.koszt + 1e-9                               # ekonomiczny nie gorszy niż standardowy


def test_determinizm():
    for views, blocks in _przypadki(seed=11, n=8):
        mk = (lambda: ([U.Widok(f"v{i}", w, h, 100.0, 10.5) for i, (w, h) in enumerate(views)],
                       [_blok_prosty(h) for h in blocks] + [_uwagi(6)]))
        a = U.rozmiesc(*mk(), 103.0, {})
        b = U.rozmiesc(*mk(), 103.0, {})
        if a is None:
            assert b is None
            continue
        assert (a.nazwa, a.W, a.H) == (b.nazwa, b.W, b.H)
        assert [r for _k, _n, r in a.roz.prostokaty] == [r for _k, _n, r in b.roz.prostokaty]


# ================================================================================================ poprawki silnika
# (zgłoszenia zespołów AR, PZT, IS, IE — docs/30_arkusze/zastosowanie_*.md)
def _blok_roza(h=30.0):
    """Blok jak „róża i podziałka”: podziałka od lewej, róża przy prawej krawędzi szerokości w."""
    def fn(sh, x, y, w):
        sh.rect(x + 4, y - 20, x + 124, y - 18)
        sh.rect(x + w - 19, y - 22, x + w - 5, y - 8)
        return y - h
    return U.blok("róża i podziałka", fn, kotwica="nad_tabliczka", w_min=155.0)


def test_znaki_centrujace_rezerwacja():
    """[PZT 1, IS 1, IE S1] Strefy znaków centrujących zajęte dla bloków; wiersz róży nad tabliczką zwężony, gdy
    prawy znak (H/2) wypada nad tabliczką (H = 297); sprawdz_nakladanie widzi blok na strefie znaku."""
    v = [U.Widok("v", 300, 200, 120, 10.5)]
    bl = [_blok_roza(), _blok_prosty(60), _uwagi(4)]
    g = U.uklady_widokow(v)[0]
    R = U.pakuj(600.0, 297.0, v, g, bl, 103.0, znaki=True)
    assert R.ok and R.znaki, R.brak
    strefy = U.strefy_znakow(600.0, 297.0)
    assert {n for k, n, _r in R.prostokaty if k == "znak"} == set("gdlp")
    for k, n, r in R.prostokaty:
        if k == "blok":
            assert not any(U._przec(r, z) for z in strefy.values()), (n, r)
    roza = [(b, r) for (b, *_x), (_k, _n, r) in zip(R.bloki, [p for p in R.prostokaty if p[0] == "blok"])
            if b.nazwa.startswith("róża")][0]
    zp = strefy["p"]
    assert roza[0].w < U.B_W and roza[1][3] > zp[1] and roza[1][2] <= zp[0] + 1e-6, roza   # zwężony, nad tabliczką
    assert abs(roza[1][0] - R.tabliczka[0]) < 1e-6
    assert not U.sprawdz_nakladanie(R)
    R.prostokaty.append(("blok", "test", (strefy["p"][0] - 5, 140.0, strefy["p"][2], 160.0)))
    assert any("znak" in e for e in U.sprawdz_nakladanie(R))
    # tryb auto: wynik nie gorszy niż bez rezerwacji; tryb „skracaj” — bez stref
    Ra = U.pakuj(600.0, 297.0, v, g, bl, 103.0)
    R0 = U.pakuj(600.0, 297.0, v, g, bl, 103.0, znaki="skracaj")
    assert Ra.ok and U._jakosc(Ra)[:3] <= U._jakosc(R0)[:3]
    assert not any(k == "znak" for k, _n, _r in R0.prostokaty)


def test_tytul_widoku_omija_znak():
    """[IS 1] Tytuł widoku trafiający na dolny znak centrujący — przesunięty w prawo za znak (w miejscu widoku)."""
    v = [U.Widok("a", 200, 255, 120, 10.5), U.Widok("b", 300, 255, 150, 10.5)]
    g = U._grupa_z_wierszy(v, [[0, 1]])
    W, H = 760.0, 297.0
    R0 = U.pakuj(W, H, v, g, [], 103.0, znaki=False)
    z = U.strefy_znakow(W, H)["d"]
    t0 = [r for k, n, r in R0.prostokaty if k == "tytul" and n == "b"][0]
    assert U._przec(t0, z), "przypadek testowy: tytuł na strefie znaku"
    R = U.pakuj(W, H, v, g, [], 103.0, znaki=True)
    t = [r for k, n, r in R.prostokaty if k == "tytul" and n == "b"][0]
    assert R.ok and R.tytuly_dx[1] > 2.0 and not U._przec(t, z), (R.tytuly_dx, t, z)
    assert t[2] <= R.widoki[1][0] + v[1].slot_w + 1e-6              # w szerokości miejsca widoku
    assert R.tytuly_dx[0] == 2.0


def test_przytnij_znaki_centrujace():
    """[PZT 1, IS 1, IE S1] Na narysowanym arkuszu znak kończy się przed treścią (odstęp 1,5 mm); gdy wejście
    < 2 mm — na ramce; bez przeszkód — 10 mm (ISO 5457 4.3); także przeszkody w rzutni."""
    from lamela.draft.core import Viewport
    from lamela.draft.sheet import ZNAK_CENTR_DL, ZNAK_CENTR_ODSTEP
    sh = Sheet("A3")                                     # 420 × 297
    x0, y0, x1, y1 = sh.frame
    W, H = sh.width, sh.height
    sh.rect(W / 2 - 10, y1 - 20, W / 2 + 10, y1 - 5, layer="R-OPISY")           # 5 mm pod ramką
    sh.text((x0 + 1.0, H / 2 - 1.0), "TEKST PRZY RAMCE", 2.5, layer="R-OPISY")  # lewy znak: < 2 mm
    vp = Viewport(100, "T")
    vp.line((0.0, 0.0), (10.0, 0.0), "A-SCIANY")                             # 100 mm w 1:100
    sh.viewports.append(vp)
    sh.place(vp, x1 - 108.0, H / 2 - 3.0, "bl", pad=3.0)                       # linia do x1 − 5 na osi H/2
    assert U.kolizje_znakow(sh), "przed przycięciem znak dotyka treści"
    gl = sh.przytnij_znaki_centrujace()
    assert abs(gl["g"] - (5.0 - ZNAK_CENTR_ODSTEP)) < 0.2, gl
    assert gl["l"] == 0.0 and gl["d"] == ZNAK_CENTR_DL, gl
    assert abs(gl["p"] - (5.0 - ZNAK_CENTR_ODSTEP)) < 0.3, gl
    assert not U.kolizje_znakow(sh)
    p = sh.znaki["g"].pts
    assert abs(p[0][1] - H) < 1e-9 and abs(p[-1][1] - (y1 - gl["g"])) < 1e-6    # od krawędzi arkusza
    assert abs(sh.znaki["l"].pts[-1][0] - x0) < 1e-9


def test_uwagi_kolejnosc_czytania():
    """[AR 1, PZT 2, IS 2, IE S2] Części uwag w kolejności czytania, ≥ 2 pozycje w części, ≤ max_czesci_uwag."""
    n_split = 0
    for views, blocks in _przypadki(seed=5, n=30):
        widoki = [U.Widok(f"v{i}", w, h, min(w, 140.0), 10.5) for i, (w, h) in enumerate(views)]
        bloki = [_blok_prosty(h) for h in blocks] + [_uwagi(12)]
        u = U.rozmiesc(widoki, bloki, 103.0, {"wysokosci": [297, 420]})
        if u is None:
            continue
        _sprawdz_uklad(u, widoki, 103.0)
        _sprawdz_czesci_uwag(u.roz, 12)
        assert u.roz.czesci_uwag <= 4
        n_split += u.roz.czesci_uwag > 1
    u = U.rozmiesc([U.Widok("v", 700, 240, 100, 10.5)], [_blok_prosty(90), _uwagi(100)], 103.0,
                   {"wysokosci": [297], "max_wysokosc": 297, "max_czesci_uwag": 6})
    _sprawdz_czesci_uwag(u.roz, 100)
    assert u.roz.czesci_uwag >= 2


def test_kara_czesci_uwag():
    """[PZT 2] Koszt = papier × składanie × (1 + kara · dodatkowe części uwag); przy dużej karze części nie
    przybywa względem kary zerowej."""
    for views, blocks in _przypadki(seed=13, n=12):
        widoki = [U.Widok(f"v{i}", w, h, min(w, 140.0), 10.5) for i, (w, h) in enumerate(views)]
        mk = lambda: [_blok_prosty(h) for h in blocks] + [_uwagi(16)]      # noqa: E731
        u0 = U.rozmiesc(widoki, mk(), 103.0, {"kara_czesci_uwag": 0.0})
        u1 = U.rozmiesc(widoki, mk(), 103.0, {"kara_czesci_uwag": 0.5})
        if u0 is None:
            continue
        assert u1.roz.dodatkowe_czesci <= u0.roz.dodatkowe_czesci, (u0.nazwa, u1.nazwa)
        k, _oc = U.koszt(u1.W, u1.H, u1.standard, U.opcje({}), 103.0)
        assert abs(u1.koszt - k * U._kara_ukladu(u1.roz, {"kara_czesci_uwag": 0.5})) < 1e-9


def test_wysrodkowanie_nie_pogarsza():
    """[PZT 3] Wyśrodkowanie grupy widoków przyjmowane tylko, gdy nie pogarsza upakowania (części uwag, kolejność,
    kolumny, liczba bloków)."""
    for views, blocks in _przypadki(seed=17, n=15):
        widoki = [U.Widok(f"v{i}", w, h, min(w, 140.0), 10.5) for i, (w, h) in enumerate(views)]
        bloki = [_blok_prosty(h) for h in blocks] + [_uwagi(10)]
        u = U.rozmiesc(widoki, bloki, 103.0, {})
        if u is None:
            continue
        r0 = U.pakuj(u.W, u.H, widoki, u.roz.grupa, bloki, 103.0)
        assert r0.ok and U._jakosc(u.roz) <= U._jakosc(r0), (u.nazwa, U._jakosc(u.roz), U._jakosc(r0))


def test_kolejnosc_kolumn():
    """[IS 3] Bloki w kilku kolumnach czytają się kolumnami od lewej, w kolumnie od góry (kolejność listy)."""
    v = [U.Widok("v", 420, 330, 150, 10.5)]
    bl = [_blok_prosty(h) for h in (110, 95, 120, 80, 100)] + [_uwagi(6)]
    u = U.rozmiesc(v, bl, 103.0, {"wysokosci": [420], "max_wysokosc": 420}, fmt="ekonomiczny")
    rects = [r for k, _n, r in u.roz.prostokaty if k == "blok"]
    assert len(U._kolumny(rects)) >= 2, rects
    assert u.roz.kolejnosc_ok and U._kolejnosc_ok(rects), [(n, r) for k, n, r in u.roz.prostokaty if k == "blok"]
    _sprawdz_uklad(u, v, 103.0)


def _teksty(sh):
    """[(napis, obwiednia (x0, y0, x1, y1))] napisów arkusza (bez rzutni)."""
    from lamela.draft.core import PText, prim_points
    out = []
    for p in sh.prims:
        if isinstance(p, PText):
            b = prim_points(p, sh.k)[0]
            out.append((p.string, (b[:, 0].min(), b[:, 1].min(), b[:, 0].max(), b[:, 1].max())))
    return out


def test_tabela_zawijanie():
    """[AR 2] ``table(zawijaj=True)``: tekst komórki dłuższy niż kolumna łamany (wiersz rośnie), bez wychodzenia
    na sąsiednią kolumnę; bez przepełnień — rysunek identyczny jak bez zawijania."""
    from lamela.draft.sheet import table
    cols = [("Nr", 14.0), ("Nazwa", 40.0), ("Posadzka", 30.0)]
    rows = [["1.01", "Pom. techniczne (centrala rekuperacyjna, wyłaz na dach)", "Deska warstwowa dębowa 15 mm, klejona"],
            ["1.02", "Hol", "Płytki"]]
    sh = Sheet("A0", draw_frame=False)
    r = table(sh, 100.0, 500.0, cols, rows, h=2.5, row_h=5.0, zawijaj=True)
    granice = [100.0, 114.0, 154.0, 184.0]
    for txt, b in _teksty(sh):
        if txt in ("Nr", "Nazwa", "Posadzka"):
            continue
        c = max(i for i in range(3) if b[0] >= granice[i] - 0.5)
        assert b[2] <= granice[c + 1] + 0.05, (txt, b, granice[c + 1])
    assert 500.0 - r[1] > 5.0 * 3 + 1.0                              # wiersz z łamaniem wyższy
    krotkie = [["1", "Hol", "Płytki"]]
    a, b = Sheet("A0", draw_frame=False), Sheet("A0", draw_frame=False)
    table(a, 10, 100, cols, krotkie)
    table(b, 10, 100, cols, krotkie, zawijaj=True)
    assert [(type(p).__name__, getattr(p, "string", None), str(getattr(p, "pts", getattr(p, "pos", None))))
            for p in a.prims] == [(type(p).__name__, getattr(p, "string", None),
                                   str(getattr(p, "pts", getattr(p, "pos", None)))) for p in b.prims]


def test_tabela_pomieszczen():
    """[AR 2] ``sheets._room_table``: długie nazwy i posadzki nie wchodzą na sąsiednie kolumny."""
    from lamela.views.sheets import _room_table
    rows = [dict(nr="3.07", nazwa="Pom. techniczne (centrala rekuperacyjna, wyłaz na dach)",
                 posadzka="Deska warstwowa dębowa 15 mm, klejona", kategoria="techniczna", wys=2.6, pow=6.1),
            dict(nr="1.13", nazwa="Garaż 2-stanowiskowy", posadzka="Posadzka żywiczna epoksydowa antypoślizgowa "
                 "R11 (garaż)", kategoria="pomocnicza", wys=2.76, pow=37.42)]
    sh = Sheet("A0", draw_frame=False)
    _room_table(rows)(sh, 50.0, 800.0, U.TB_W)
    granice = [50.0]
    for w in (14.0, 60.0, 46.0, 18.0, 18.0, 22.0):
        granice.append(granice[-1] + w)
    for txt, b in _teksty(sh):
        if b[3] > 800.0 - 7.0 - 0.1 or txt.startswith("ZESTAWIENIE"):
            continue                                     # tytuł i nagłówek
        c = max(i for i in range(6) if b[0] >= granice[i] - 0.6)
        assert b[2] <= granice[c + 1] + 0.05, (txt, b, granice[c + 1])


def test_zamiennik_glifu():
    """[AR 3] ⌀ (U+2300, brak w Liberation Sans) → Ø w pomiarze, PDF i DXF; QA ostrzega o znakach spoza kroju."""
    from lamela.draft import plot
    from lamela.draft import text as T
    from lamela.draft.core import text_items
    from lamela.draft.sheet import TitleBlock
    assert T.normalizuj("pręty ⌀12") == "pręty Ø12" and T.brakujace_znaki("pręty ⌀12") == ""
    assert abs(T.width("⌀12", 2.5) - T.width("Ø12", 2.5)) < 1e-9
    sh = Sheet("A3", title_block=TitleBlock(tytul="T", skala="1:50", nr_rysunku="X", obiekt="O", data="d"))
    p = sh.text((50, 50), "pręty ⌀12", 2.5, layer="R-OPISY")
    assert [s_ for _xy, s_, _h in text_items(p, 1.0)[0]] == ["pręty Ø12"]
    sh.text((50, 60), "kąt ∠ 30°", 2.5, layer="R-OPISY")
    w = plot.qa(sh)["warnings"]
    assert any("∠" in x for x in w) and not any("⌀" in x or "Ø" in x for x in w), w


def test_spis_rysunkow_tomu():
    """[IE S3, S4] Spis w tomie: nagłówek łamany do szerokości pola (pismo 5 → 3,5 mm), tytuły rysunków łamane
    w komórce, nic nie dotyka znaków centrujących."""
    from lamela.draft import plot
    from lamela.draft.sheet import ZNAK_CENTR_DL, TitleBlock
    tyt = ["INSTALACJA FOTOWOLTAICZNA — SCHEMAT, ZABEZPIECZENIA I POŁĄCZENIA (FALOWNIK, SPD)",
           "INSTALACJA ODGROMOWA I POŁĄCZENIA WYRÓWNAWCZE KONSTRUKCJI PV — RZUT DACHU"] + ["RZUT"] * 12
    arks = [Sheet("A3", title_block=TitleBlock(tytul=t, nr_rysunku=f"PT-IE-{i + 1:02d}", skala="1:50"))
            for i, t in enumerate(tyt)]
    sh = plot.spis_rysunkow(arks, "Projekt techniczny — instalacje elektryczne wewnętrzne i zewnętrzne, "
                                  "fotowoltaika, ochrona odgromowa (rysunki)")
    x0, y0, x1, y1 = sh.frame
    lo, hi = x0 + ZNAK_CENTR_DL, x1 - ZNAK_CENTR_DL
    for txt, b in _teksty(sh):
        if b[1] > sh.tb_rect[3]:                         # treść spisu (nad tabliczką)
            assert lo < b[0] and b[2] < hi, (txt, b)
            assert b[3] < y1 - ZNAK_CENTR_DL, (txt, b)
    assert not U.kolizje_znakow(sh), U.kolizje_znakow(sh)
    assert sh.znaki_gl["g"] == ZNAK_CENTR_DL and sh.znaki_gl["l"] == ZNAK_CENTR_DL


def test_odcinek_kontrolny_a_znak():
    """Odcinek kontrolny 100 mm w marginesie na oprawę: napis nie przecina lewego znaku centrującego (H = 297)."""
    from lamela.draft import plot
    for fmt_ in ("A3", "710x420", "A4"):
        sh = Sheet(fmt_)
        plot.add_control_marks(sh)
        cy = sh.height / 2.0
        (xa, _ya), (xb, _yb) = sh.znaki["l"].pts[0], sh.znaki["l"].pts[-1]
        for txt, b in _teksty(sh):
            if txt.startswith("odcinek kontrolny"):
                assert not (b[1] < cy + 0.35 and b[3] > cy - 0.35 and b[0] < xb and b[2] > xa), (fmt_, b)


def test_metryka_skladowe():
    """[AR 4] ``tools/metryki_arkuszy.py``: W skł. rozbija składową wklęsłą (bloki sklejone domknięciem 6 mm
    w „L”) i pokazuje puste pole, które W obw. zamyka w jednej obwiedni."""
    import importlib.util
    import tempfile
    spec = importlib.util.spec_from_file_location("_metryki_test", ROOT / "tools" / "metryki_arkuszy.py")
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    sh = Sheet("600x420")
    for x0, y0, x1, y1 in ((30, 200, 400, 400), (406, 20, 580, 400)):     # „L”: odstęp 6 mm, puste pole w rogu
        sh.rect(x0, y0, x1, y1, layer="R-OPISY")
        for k in range(1, 8):
            sh.line((x0, y0 + k * (y1 - y0) / 8), (x1, y0 + k * (y1 - y0) / 8), layer="R-OPISY")
    with tempfile.TemporaryDirectory() as d:
        files = sh.save(Path(d) / "L", formats=("pdf",))
        r = M.analyze_pdf(Path(files["pdf"]))
    assert r["wypelnienie"] > 0.9 and r["wypelnienie_skl"] < r["wypelnienie"] - 0.2, (r["wypelnienie"],
                                                                                      r["wypelnienie_skl"])


# ================================================================================================ arkusze z modelu
_CTX = None


def _ctx():
    global _CTX
    if _CTX is None:
        from lamela.ir import build_ir
        from lamela.model import load_model
        from lamela.views.sheets import load_config, make_context
        m = load_model(B_TEST, D_TEST, strict=False)
        ir = build_ir(m, otoczenie=True, auta=False)
        cfg = load_config(ROOT / "model" / "test" / "arkusze_testowe.yaml", m)
        _CTX = make_context(m, ir, cfg, [], src=str(B_TEST))
    return _CTX


def _rejestruj_widok_testowy():
    """Widok rejestrowany (kontrakt ``register_view``) z blokami kolumny, uwagą jednostek i schematem bez skali."""
    from types import SimpleNamespace

    from lamela.draft.core import Viewport
    from lamela.views.sheets import register_view

    def blk(h):
        def fn(sh, x, y, w):
            with sh.on("R-LEGENDA"):
                sh.text((x, y - 3.5), f"LEGENDA TESTOWA {h}", 3.5, style="bold")
                sh.rect(x, y - h, x + w, y - 6)
            return y - h
        return fn

    def widok(ctx, spec, scale, opts):
        vp = Viewport(scale, spec.get("tytul_widoku") or "SCHEMAT TESTOWY")
        L = float(opts.get("dl", 12.0))
        with vp.on("A-WIDOK"):
            vp.rect(0, 0, L, 6.0)
            vp.line((0, 0), (L, 6.0))
            vp.text((0.2, 6.5), "opis", 2.5)
        res = SimpleNamespace(column_blocks=[("leg1", blk(60)), ("leg2", blk(45))],
                              notes=["Uwaga widoku testowego."], units_note="Jednostki testowe: wymiary w m.",
                              bez_skali=bool(opts.get("bez_skali", False)), north=False)
        return vp, res, vp.title

    register_view("test_uklad", widok, rodzaj="rysunek testowy", qa="PZT")


def _build(spec):
    from lamela.views.sheets import build_sheet
    return build_sheet(_ctx(), dict(spec), 1, 1)


def test_widok_rejestrowany():
    _rejestruj_widok_testowy()
    sh, info = _build({"nr": "T-U-01", "tytul": "TEST", "typ": "test_uklad", "skala": 100,
                       "opcje": {"bez_skali": True, "dl": 30.0}})
    assert info["qa_kind"] == "PZT" and info["skala"] == "—" and sh.tb.skala == "—"
    assert info["uklad"]["tryb"] == "ekonomiczny" and not info["uklad"]["kolizje"], info["uklad"]
    assert (round(sh.width, 1), round(sh.height, 1)) == tuple(info["wymiary_mm"])
    assert info["skladanie"]["tabliczka_na_wierzchu"]
    names = [n for n, _r in info["uklad"]["bloki"]]
    assert "leg1" in names and "leg2" in names and any(n.startswith("uwagi") for n in names), names
    assert not any(n.startswith("róża") or n == "podziałka" for n in names), "schemat bez skali — bez podziałki"
    txt = " ".join(p.string for p in sh.prims if hasattr(p, "runs"))
    assert "Jednostki testowe" in txt and "Uwaga widoku testowego" in txt


def test_zgodnosc_wsteczna_arkusz():
    """Format jawny działa jak dotąd; tryb klasyczny = dawny algorytm; format [H, L] — niestandardowy."""
    from lamela.views.sheets import FORMATS
    _rejestruj_widok_testowy()
    base = {"nr": "T-U-02", "tytul": "TEST", "typ": "test_uklad", "skala": 50, "opcje": {"dl": 20.0}}
    sh, info = _build(dict(base, format="A2"))
    assert info["format"] == "A2" and (sh.width, sh.height) == (594, 420)
    sh, info = _build(dict(base, format="A3x3"))
    assert info["format"] == "A3×3" and (sh.width, sh.height) == (891, 420)
    sh, info = _build(dict(base, format="klasyczny"))
    assert info["uklad"]["tryb"] == "klasyczny" and info["format"] in FORMATS
    sh, info = _build(dict(base, format=[594, 700]))
    assert (sh.width, sh.height) == (700.0, 594.0) and sh.fmt_name == "700×594"
    sh, info = _build(dict(base, format="A4"))                # za mały → układ klasyczny z uwagą (jak dotąd)
    assert info["format"] == "A4"
    sh, info = _build(dict(base, format=[297, 300]))          # [H, L] za mały → układ klasyczny, ten sam format
    assert (sh.width, sh.height) == (300.0, 297.0) and info["uklad"]["tryb"] == "klasyczny"


def test_arkusz_rzutu_z_modelu():
    """Rzut parteru modelu testowego: układ ekonomiczny bez kolizji, QA bez błędów, tabliczka na wierzchu."""
    from lamela.draft import plot
    spec = next(s for s in ctx_cfg_arkusze() if s["nr"] == "T-AR-01")
    sh, info = _build(spec)
    assert not info["uklad"]["kolizje"], info["uklad"]["kolizje"]
    qa = plot.qa(sh, kind=info.get("qa_kind"))
    assert qa["ok"], qa["errors"][:5]
    assert info["skladanie"]["tabliczka_na_wierzchu"]
    assert info["uklad"]["wypelnienie_szac"] > 0.45, info["uklad"]
    tb = sh.tb_rect
    assert abs(tb[2] - sh.frame[2]) < 1e-6 and abs(tb[1] - sh.frame[1]) < 1e-6
    sh2, info2 = _build(spec)                                    # determinizm
    assert info2["uklad"]["bloki"] == info["uklad"]["bloki"] and info2["format"] == info["format"]


def test_widoki_nr_i_scalanie_blokow():
    """[IS 4, IS 5] Widoki z listy ``widoki`` dziedziczą ``nr`` arkusza; bloki kolumny o tej samej nazwie i treści
    z kilku widoków — raz, o tej samej nazwie i innej treści — oba."""
    from types import SimpleNamespace

    from lamela.draft.core import Viewport
    from lamela.views.sheets import register_view
    nry = []

    def leg(sh, x, y, w):
        sh.text((x, y - 3.5), "LEGENDA WSPÓLNA", 3.5)
        sh.rect(x, y - 30, x + w, y - 6)
        return y - 30

    def tab(i):
        def fn(sh, x, y, w):
            sh.text((x, y - 3.5), f"TABELA KONDYGNACJI {i}", 3.5)
            return y - 20
        return fn

    def widok(ctx, spec, scale, opts):
        nry.append(spec.get("nr"))
        vp = Viewport(scale, "SCHEMAT")
        vp.rect(0, 0, 8.0, 5.0, "A-WIDOK")
        return vp, SimpleNamespace(column_blocks=[("leg", leg), ("tab", tab(spec.get("i")))], notes=[],
                                   bez_skali=True, north=False), vp.title

    register_view("test_scal", widok, rodzaj="rysunek testowy", qa="PZT")
    sh, info = _build({"nr": "T-S-01", "tytul": "TEST", "skala": 100,
                       "widoki": [{"typ": "test_scal", "i": 1}, {"typ": "test_scal", "i": 2}]})
    assert nry == ["T-S-01", "T-S-01"], nry
    names = [n for n, _r in info["uklad"]["bloki"]]
    assert names.count("leg") == 1 and names.count("tab") == 2, names
    txt = [p.string for p in sh.prims if hasattr(p, "runs")]
    assert txt.count("LEGENDA WSPÓLNA") == 1 and {"TABELA KONDYGNACJI 1", "TABELA KONDYGNACJI 2"} <= set(txt)
    assert not info["uklad"]["kolizje"] and set(info["uklad"]["znaki_centrujace"]) == set("gdlp")


# ================================================================================================ poprawki po weryfikacji
# (docs/30_arkusze/weryfikacja_M.md § 3, weryfikacja_C.md 2.7, 2.10)
def test_szerokosc_rolki():
    """[M § 3] Kandydaci „szerokość = rolka, wysokość docięta”: treść ~560×400 mm dostaje 594×H (pasy 210 + 192 +
    192), a nie 690×420 (pasy 140 + 120 + 120 + 120 + 190); bez rolek (``rolki: []``) koszt nie jest mniejszy."""
    v = [U.Widok("v", 400, 300, 150, 10.5)]
    mk = lambda: [_blok_prosty(90), _uwagi(8)]          # noqa: E731
    u = U.rozmiesc(v, mk(), 103.0, {})
    assert (u.W, u.H) == (594.0, 440.0), (u.nazwa, u.kandydaci)
    assert u.skladanie["pasy"] == [210.0, 192.0, 192.0], u.skladanie
    _sprawdz_uklad(u, v, 103.0)
    u0 = U.rozmiesc(v, mk(), 103.0, {"rolki": []})
    assert u0.koszt >= u.koszt - 1e-9 and u0.W * u0.H >= u.W * u.H, (u0.nazwa, u.nazwa)
    # max_wysokosc ogranicza także wysokość arkusza „bokiem na rolkę”
    u1 = U.rozmiesc(v, mk(), 103.0, {"max_wysokosc": 420})
    assert u1.H <= 420.0 + 1e-6, u1.nazwa
    h = U.min_wysokosc(594.0, v, U.uklady_widokow(v), mk(), 103.0, U.opcje({}))
    assert h is not None and h[2].ok and h[0] <= 440.0, h


def test_bloki_odsuniete_od_ramki():
    """[C 2.10] Bloki kolumny opisowej ≥ 3 mm od prawej ramki (szer. 177 mm, lewa krawędź jak tabliczka); tytuł
    widoku ≥ 4 mm od znaku centrującego."""
    v = [U.Widok("v", 300, 200, 120, 10.5)]
    for u in (U.rozmiesc(v, [_blok_roza(), _blok_prosty(60), _uwagi(6)], 103.0, {}),
              U.rozmiesc(v, [_blok_prosty(150), _blok_prosty(120), _uwagi(20)], 103.0, {"wysokosci": [297],
                                                                                          "rolki": []})):
        fx0, fy0, fx1, fy1 = U.rama(u.W, u.H)
        for k, n, r in u.roz.prostokaty:
            if k == "blok":
                assert r[2] <= fx1 - U.PAD_B + 1e-6, (n, r, fx1)
        _sprawdz_uklad(u, v, 103.0)
    w = [U.Widok("a", 200, 150, 150, 10.5), U.Widok("b", 200, 150, 150, 10.5)]
    g = U._grupa_z_wierszy(w, [[0, 1]])
    W, H = 2 * (U.MARG_L + U.PAD_V) + g.w, 297.0
    ox = W / 2.0 - (g.poz[1][0] + 1.0)                   # tytuł widoku „b” tuż za znakiem dolnym (oś W/2)
    dx = U._tytuly_od_znakow(w, g, ox, U.MARG + U.PAD_B, U.strefy_znakow(W, H))
    x_t = ox + g.poz[1][0] + dx[1]
    assert dx[1] > 2.0 and x_t - (W / 2.0 + 0.35) >= U.ODST_TYTUL_ZNAK - 1e-6, (dx, x_t, W / 2.0)


def test_siatka_formaty_niestandardowe():
    """[C 2.7] Siatka odniesień na wszystkich arkuszach o dłuższym boku > 420 mm (także 690×297, 580×420)."""
    for f, jest in (("690x297", True), ("580x420", True), ("A3", False), ("A2", True), ("420x477", True)):
        sh = Sheet(f)
        assert bool(getattr(sh, "_siatka_dol", False)) == jest, f


def ctx_cfg_arkusze():
    from lamela.views.sheets import load_config
    return load_config(ROOT / "model" / "test" / "arkusze_testowe.yaml", _ctx().model)["arkusze"]


# ==================================================================================================
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--szybko", action="store_true", help="bez arkuszy z modelu testowego")
    a = ap.parse_args(argv)
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    if a.szybko:
        tests = [(n, f) for n, f in tests if n not in ("test_widok_rejestrowany", "test_zgodnosc_wsteczna_arkusz",
                                                       "test_arkusz_rzutu_z_modelu",
                                                       "test_widoki_nr_i_scalanie_blokow")]
    ok = fail = 0
    t0 = time.time()
    for n, f in tests:
        t1 = time.time()
        try:
            f()
            ok += 1
            print(f"PASS  {n}  ({time.time() - t1:.1f} s)", flush=True)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"FAIL  {n}: {e}", flush=True)
            traceback.print_exc(limit=4)
    print(f"\n{ok} zaliczonych, {fail} niezaliczonych, czas {time.time() - t0:.0f} s")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
