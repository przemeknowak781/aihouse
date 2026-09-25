#!/usr/bin/env python3
"""Testy silnika ekonomicznego ustawienia na arkuszach (``lamela.views.uklad``, ``lamela.draft.skladanie``).

Sprawdza: pasy składania do A4 (harmonijka: pasy ≤ 210 mm, w parach równych, pas z tabliczką ≥ 190 mm na
wierzchu, pasy „ładne” 180–210 mm), plan składania (``plan_skladania``), formaty niestandardowe arkusza, podział
uwag, brak nakładania bloków i widoków, zgodność wsteczną (formaty jawne, tryb klasyczny, kontrakt
``register_view``: column_blocks, units_note, bez_skali, qa) i determinizm.

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
        if W > 590.5:
            assert pasy[0] == 210.0, (W, pasy)
            mid = pasy[1:]
            for i in range(0, len(mid), 2):              # pary równe (warunek zamknięcia harmonijki)
                assert abs(mid[i] - mid[i + 1]) < 1e-6, (W, pasy)
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
    assert SK.ocena_skladania(780, 297)["ocena_pion"] == "słabe"          # n nieparzyste: para 95 mm


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
    labels = [p.string for p in sh.prims if hasattr(p, "runs") and p.pos[1] < 3.0]
    assert sorted(labels) == [str(i + 1) for i in range(len(xs))], labels
    txt = [p.string for p in sh.prims if hasattr(p, "runs")]
    assert any("format niestandardowy" in t for t in txt)
    assert not Sheet("A3x3").custom and Sheet("A3x3").fmt_name == "A3×3"
