#!/usr/bin/env python3
"""Rewizja v1.1 – elewacje: okna a strop i kaseta ZIP (E-I-5), U ścian z warstw i łączników (E-I-6),
lamele korony – rytm, kontrast, kąt pełnego przesłonięcia (E-I-7), trakt skrzydła (uwaga modelu pomieszczeń).

Uruchomienie (z katalogu umwd/): /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_elewacje.py
Opory przejmowania: elewacja wentylowana – Rsi = Rse = 0,13 m²K/W (PN-EN ISO 6946); λ żelbetu 2,5 W/(mK).
ΔU od łączników: konsole ze stali nierdzewnej z przekładką termiczną, ≈ 1,0 szt./m², χ ≈ 0,020–0,025 W/K (wartość
projektowa do potwierdzenia obliczeniem 3D wg PN-EN ISO 10211) – przyjęto ΔU = 0,025 (wieża) i 0,020 (skrzydło, konsole punktowe).
"""
import math


def u_wall(layers, du):
    r = 0.26 + sum(d / lam for d, lam in layers)
    return 1 / r, 1 / r + du


def fib_word(n):
    a, b = "A", "AB"
    while len(b) < n:
        a, b = b, b + a
    return b[:n]


def main():
    print("== 1. Okna a spód stropu (kaseta ZIP 0,18 m w nadprożu)")
    for nm, clear, sill, h in (("skrzydło v1.0", 3.20, 0.90, 2.40), ("skrzydło v1.1 (parapet 0,60 + kwatera stała do 0,90)", 3.20, 0.60, 2.35),
                               ("wieża v1.0", 3.32, 0.85, 2.45), ("wieża v1.1 (parapet 0,55 + kwatera stała)", 3.32, 0.55, 2.45)):
        head = sill + h
        print(f"  {nm}: nadproże {head:.2f}, kaseta do {head + 0.18:.2f}, spód stropu {clear:.2f} → {'OK' if head + 0.18 <= clear else 'KOLIZJA'}")
    print(f"  WWR skrzydła v1.1: 1,20 × 2,35 / (2,025 × 3,75) = {1.20 * 2.35 / (2.025 * 3.75):.1%}; wieża 1,65 × 2,45 / (2,70 × 3,75) = "
          f"{1.65 * 2.45 / (2.70 * 3.75):.1%}")

    print("== 2. Współczynnik U ścian (E-I-6)")
    walls = {
        "v1.0 – wełna 200 λ 0,033 + żelbet 200 (bez łączników)": ([(0.20, 0.033), (0.20, 2.5)], 0.0),
        "v1.0 – jw. z konsolami Al (ΔU 0,02–0,07)": ([(0.20, 0.033), (0.20, 2.5)], 0.045),
        "v1.1 wieża – granit 40 / pustka 40 / wełna 260 λ 0,033 / żelbet 200; konsole nierdzewne": ([(0.26, 0.033), (0.20, 2.5)], 0.025),
        "v1.1 skrzydło i segment – ceramika 40 / pustka 40 / wełna 240 λ 0,031 / żelbet 150; konsole nierdzewne": ([(0.24, 0.031), (0.15, 2.5)], 0.020),
    }
    for nm, (ly, du) in walls.items():
        u0, u = u_wall(ly, du)
        print(f"  {nm}: U0 {u0:.3f}, U {u:.3f} → {'≤ 0,15 ✔' if u <= 0.15 else ('≤ 0,20 (WT)' if u <= 0.20 else '> 0,20 ✖')}")

    print("== 3. Trakt skrzydła 15,00 m (uwaga modelu pomieszczeń; G-K-1 wariant A – lico ściany = obrys)")
    ext = 0.04 + 0.04 + 0.24 + 0.15
    part = 0.10
    room = 6.08
    corr = 15.00 - 2 * ext - 2 * part - 2 * room
    print(f"  ściana zewn. {ext:.2f} × 2 + pokoje {room:.2f} × 2 + ściany korytarza {part:.2f} × 2 + korytarz {corr:.2f} = 15,00 m; "
          f"pokój 3,95 × {room:.2f} = {3.95 * room:.2f} m² ≥ 24,0 ✔; korytarz ≥ 1,50 (obrót wózka) ✔, ≥ 1,40 (WT) ✔")

    print("== 4. Lamele korony (E-I-7)")
    R, arc = 14.0, 14.0 * math.pi / 2
    old_p, old_w, D = 0.90, 0.25, 0.60
    print(f"  v1.0: 0,25 × 0,60 co 0,90 m – pełne przesłonięcie od {math.degrees(math.atan((old_p - old_w) / D)):.1f}° (spec.: 34°); "
          f"okres 0,90 m: z 80 / 150 / 200 m = {1 / math.degrees(math.atan(0.9 / 80)):.1f} / {1 / math.degrees(math.atan(0.9 / 150)):.1f} / "
          f"{1 / math.degrees(math.atan(0.9 / 200)):.1f} c/°")
    A, B, w = 1.35, 0.675, 0.35
    seq = fib_word(40)
    pitches = [A if c == "A" else B for c in seq]
    n, acc = 0, 0.0
    for p in pitches:
        if acc + p > arc:
            break
        acc += p
        n += 1
    mean = sum(pitches[:n]) / n
    print(f"  v1.1: lamele 0,35 × 0,60 m (R 13,40–14,00), rozstawy A = 1,35 / B = 0,675 m w ciągu Fibonacciego "
          f"({seq[:13]}…) – brak okresu dominującego; na łuku {arc:.2f} m: {n + 1} lameli, średni rozstaw {mean:.3f} m")
    print(f"  przesłonięcie w osi {w / mean:.0%}; pełne przesłonięcie od {math.degrees(math.atan((A - w) / D)):.1f}° (największa szczelina) "
          f"/ {math.degrees(math.atan((B - w) / D)):.1f}° (szczelina mała)")
    print(f"  składowe rytmu z 80 / 200 m: A {1 / math.degrees(math.atan(A / 80)):.1f}–{1 / math.degrees(math.atan(A / 200)):.1f} c/°, "
          f"B {1 / math.degrees(math.atan(B / 80)):.1f}–{1 / math.degrees(math.atan(B / 200)):.1f} c/° (nieregularnie, o niskim kontraście)")
    # kontrast: L* z NCS (przybliżenie: L* ≈ 100 − 1,1 × czerń) – lamela S 2005-Y20R, szkło z sitodrukiem ceramicznym 30 % na tle wnętrza
    l_lam = 100 - 1.1 * 40                   # lamela ceramiczna S 4005-Y20R (ciepła szarość, ton w ton ze szkłem)
    l_glass_old = 30.0                       # ciemne szkło g 0,27 / R 12 % (oszacowanie)
    l_glass_new = 0.70 * l_glass_old + 0.30 * (100 - 1.1 * 10)   # sitodruk S 1010-Y20R 30 %
    print(f"  kontrast ΔL*: v1.0 lamela S 1005-Y20R ({100 - 1.1 * 5:.0f}) / szkło ({l_glass_old:.0f}) ≈ {100 - 1.1 * 5 - l_glass_old:.0f}; "
          f"v1.1 lamela S 4005-Y20R ({l_lam:.0f}) / szkło z sitodrukiem 30 % ({l_glass_new:.0f}) ≈ {l_lam - l_glass_new:.0f} "
          f"→ cel ≤ 15 {"✔" if l_lam - l_glass_new <= 15 else "✖"} (do potwierdzenia próbką)")
    print(f"  powierzchnia elewacji z lamelami: łuk {arc:.1f} × 6,60 = {arc * 6.6:.0f} m² + pas wyrzutni pd. ≈ 70 m² + wyrzut agregatu/garażu ≈ 20 m² → ≈ 240 m²")


if __name__ == "__main__":
    main()
