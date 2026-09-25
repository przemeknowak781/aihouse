"""Składanie arkuszy do formatu A4 (wersja papierowa, RPB § 2a) — geometria harmonijki i ocena „ładnego” składania.

Model [przyjęcie — praktyka DIN 824:1981-03, forma A „do wpięcia”, uogólniona na formaty wydłużone i niestandardowe;
PN-N-01603:1986 — wycofana bez następcy, przywołanie informacyjne]:

* najpierw zgięcia **pionowe** (harmonijka), potem **poziome** co 297 mm od dołu;
* paczka ma szerokość 210 mm; pierwszy pas (lewy, z marginesem 20 mm na oprawę) leży na spodzie licem do góry
  z marginesem przy lewej krawędzi paczki; pas z tabliczką (prawy, ≥ 190 mm) — na wierzchu licem do góry na
  [20, 210] mm paczki, tabliczka w prawym dolnym rogu;
* w harmonijce pasy leżą na przemian licem do góry i do dołu, więc liczba pasów musi być **nieparzysta**; zgięcia
  między pasami 2…N leżą w paczce w [0, 210] (pas ≤ 190 mm w [20, 210] nie zasłania marginesu na oprawę).
  Warunek zamknięcia: prawa krawędź arkusza wraca do x = 210 mm paczki.

Rodziny pasów (``warianty_pasow``; wybór: najlepsza ocena, potem mniej pasów, potem pierwszy pas 210 mm):

* W ≤ 210 mm — bez zgięć pionowych;
* **A** (jak dotąd, praktyka DIN): [210, p par równych]: wszystkie pary w = (W − 210)/(2p), gdy 190 ≤ w ≤ 210,
  inaczej para z tabliczką 190 mm i pozostałe pary równe (≤ 210 mm) — A2: 210 + 192 + 192; A3×3: 210 + 150,5 +
  150,5 + 190 + 190; A1: 210 + 125,5 + 125,5 + 190 + 190 (dla formatów ISO bez zmian);
* **B** (zygzak w pasie [20, 20 + m]): [20 + m, m × (2k − 1), 190], m = (W − 210)/(2k) ≤ 190 — pierwszy pas węższy
  niż 210 mm, pozostałe równe i nie zasłaniają marginesu; k = 1 to klasyczne A3 (125 + 105 + 190; dawniej
  105 + 125 + 190 — margines wypadał wewnątrz paczki). Dla szerokości 630–970 mm B daje pasy 105–190 mm zamiast
  wąskiej pary A (np. 690: 140 + 120 + 120 + 120 + 190 zamiast 210 + 50 + 50 + 190 + 190).
  Wniosek: L = 210 + 190·n składa się pasami 190 mm tylko dla parzystego n (590, 970, 1350 … mm).

Ocena (``ocena_skladania``) — te same progi co ``tools/metryki_arkuszy.py`` (fold_plan), plus warunek „tabliczka na
wierzchu” (pas z tabliczką ≥ 190 mm, dolny rząd ≥ wysokość tabliczki + 10 mm).
"""
from __future__ import annotations

from functools import lru_cache

A4_W, A4_H = 210.0, 297.0
PAS_OPRAWY = 210.0          # pierwszy pas (z marginesem na oprawę) — rodzina A
MARGINES_OPRAWY = 20.0
PAS_TABLICZKI = 190.0       # pas z tabliczką (szer. tabliczki 180 + margines 10)
PAS_MAX = 210.0
RANK = {"dobre": 2, "poprawne": 1, "słabe": 0}


def ocena_pionowa(pasy: list[float], W: float) -> tuple[str, list[str]]:
    """Ocena pasów pionowych (progi ``tools/metryki_arkuszy.py``): pasy pośrednie 180–210 mm i równe (rozrzut
    ≤ 5 mm) → dobre, ≥ 120 mm → poprawne, węższe → słabe; W ≤ 420 mm — klasyczne A3 (≥ 400 mm: dobre)."""
    uw = []
    if W <= A4_W + 0.5:
        return "dobre", uw
    if W <= 2 * A4_W + 0.5:
        ov = "dobre" if W >= 399.5 else ("poprawne" if min(pasy) >= 60.0 else "słabe")
        if W < 399.5:
            uw.append(f"pas pośredni {pasy[1]:.0f} mm (klasyczne A3: 105 mm)")
    else:
        mid = pasy[1:-1] if len(pasy) > 2 else pasy
        rozrzut = max(mid) - min(mid)
        ov = "dobre" if (min(mid) >= 180 and rozrzut <= 5.0) else ("poprawne" if min(mid) >= 120 else "słabe")
        if min(mid) < 180:
            uw.append(f"najwęższy pas pośredni {min(mid):.0f} mm")
        if rozrzut > 5.0:
            uw.append(f"pasy nierówne (rozrzut {rozrzut:.0f} mm)")
    if max(pasy) > PAS_MAX + 0.5:
        ov = "słabe"
        uw.append(f"paczka szersza niż A4 ({max(pasy):.0f} mm)")
    if pasy[-1] < PAS_TABLICZKI - 0.5:
        uw.append(f"pas z tabliczką {pasy[-1]:.0f} mm < 190 mm — tabliczka częściowo pod spodem")
        ov = min(ov, "poprawne", key=lambda o: RANK[o])
    return ov, uw


def warianty_pasow(W: float) -> list[list[float]]:
    """Wszystkie poprawne geometrycznie harmonijki dla szerokości W > 210 mm (rodziny A i B)."""
    out = []
    rest = W - PAS_OPRAWY
    for p in range(1, 200):                                            # A: [210, pary]
        w = rest / (2 * p)
        if PAS_TABLICZKI - 1e-6 <= w <= PAS_MAX + 1e-6:
            out.append([PAS_OPRAWY] + [w] * (2 * p))
        elif p > 1:
            a = (rest - 2 * PAS_TABLICZKI) / (2 * (p - 1))
            if 0 < a <= PAS_MAX + 1e-6:
                out.append([PAS_OPRAWY] + [a] * (2 * (p - 1)) + [PAS_TABLICZKI] * 2)
        if w < 20.0:
            break
    for k in range(1, 200):                                            # B: [20 + m, m…, 190]
        m = (W - MARGINES_OPRAWY - PAS_TABLICZKI) / (2 * k)
        if m <= 0 or m < 20.0 and k > 1:
            break
        if m <= PAS_TABLICZKI + 1e-6:
            out.append([MARGINES_OPRAWY + m] + [m] * (2 * k - 1) + [PAS_TABLICZKI])
    return out


@lru_cache(maxsize=4096)
def _pasy(W: float) -> tuple:
    if W <= A4_W + 0.5:
        return (W,)
    best = None
    for c in warianty_pasow(W):
        ov, _u = ocena_pionowa(c, W)
        din = 0 if abs(c[0] - PAS_OPRAWY) < 1e-6 or ov == "słabe" else 1     # remis: pierwszy pas 210 (DIN)
        key = (-RANK[ov], len(c), din, -round(min(c[1:-1] or c), 3))
        if best is None or key < best[0]:
            best = (key, c)
    return tuple(best[1]) if best else (W,)


def pasy_pionowe(W: float) -> list[float]:
    """Szerokości pasów harmonijki od lewej krawędzi [mm] (suma = W): najlepiej oceniony wariant z
    ``warianty_pasow``; remis — mniej pasów, potem pierwszy pas 210 mm (praktyka DIN; przy ocenie „słabe” — najszerszy
    najwęższy pas). W zaokrąglane do 0,01 mm —
    wymiary odczytane z PDF (np. 630,0000037) dają ten sam plan co wymiary nominalne."""
    return list(_pasy(round(float(W), 2)))


def rzedy_poziome(H: float) -> list[float]:
    """Wysokości rzędów od dolnej krawędzi [mm]: co 297 mm, ostatni (górny) — reszta."""
    H = round(float(H), 2)
    ys = []
    y = A4_H
    if H > A4_H + 0.5:
        while y < H - 1.0:
            ys.append(y)
            y += A4_H
    edges = [0.0] + ys + [H]
    return [b - a for a, b in zip(edges[:-1], edges[1:])]


def fold_positions(W: float, H: float):
    """Linie składania: (xs od lewej krawędzi, ys od dolnej krawędzi) [mm]."""
    xs, x = [], 0.0
    for w in pasy_pionowe(W)[:-1]:
        x += w
        xs.append(round(x, 3))
    ys, y = [], 0.0
    for h in rzedy_poziome(H)[:-1]:
        y += h
        ys.append(round(y, 3))
    return xs, ys


def ocena_skladania(W: float, H: float, tb_h: float | None = None) -> dict:
    """Plan i ocena składania („dobre” | „poprawne” | „słabe”) — progi jak w ``tools/metryki_arkuszy.py``.

    ``tb_h`` — wysokość tabliczki z tabelą zmian [mm] (sprawdzenie, czy mieści się w dolnym rzędzie)."""
    xs, ys = fold_positions(W, H)
    pasy = pasy_pionowe(W)
    rzedy = rzedy_poziome(H)
    ov, uw = ocena_pionowa(pasy, W)
    na_wierzchu = W <= A4_W + 0.5 or pasy[-1] >= PAS_TABLICZKI - 0.5
    last = rzedy[-1]
    if len(rzedy) == 1 or last >= 0.9 * A4_H:
        oh = "dobre"
    elif last >= 0.35 * A4_H:
        oh = "poprawne"
        uw.append(f"górny rząd {last:.0f} mm (niepełny)")
    else:
        oh = "słabe"
        uw.append(f"górny rząd tylko {last:.0f} mm (wąski pasek)")
    if tb_h is not None and rzedy[0] < tb_h + 10.0 - 1e-6:
        na_wierzchu = False
        uw.append(f"tabliczka ({tb_h:.0f} mm) wyższa niż dolny rząd {rzedy[0]:.0f} mm")
    ocena = min((ov, oh), key=lambda o: RANK[o])
    return dict(zgiecia_pionowe=[round(x, 1) for x in xs], zgiecia_poziome=[round(y, 1) for y in ys],
                pasy=[round(p, 1) for p in pasy], rzedy=[round(r, 1) for r in rzedy], n_pasow=len(pasy),
                n_rzedow=len(rzedy), warstwy=len(pasy) * len(rzedy), ocena=ocena, ocena_pion=ov, ocena_poziom=oh,
                tabliczka_na_wierzchu=bool(na_wierzchu), uwagi=uw)


def opis_skladania(W: float, H: float) -> str:
    """Opis słowny planu składania (do wykazu rysunków / plan_skladania)."""
    o = ocena_skladania(W, H)
    if o["n_pasow"] == 1 and o["n_rzedow"] == 1:
        return "bez składania (A4)"
    s = []
    if o["n_pasow"] > 1:
        s.append(f"harmonijka {' + '.join(f'{p:.0f}' for p in o['pasy'])} mm (pierwszy pas z marginesem 20 mm "
                 f"do oprawy, pas z tabliczką na wierzchu)")
    if o["n_rzedow"] > 1:
        s.append(f"zgięcia poziome: rzędy {' + '.join(f'{r:.0f}' for r in o['rzedy'])} mm od dołu")
    return "; ".join(s) + f" — ocena: {o['ocena']}"
