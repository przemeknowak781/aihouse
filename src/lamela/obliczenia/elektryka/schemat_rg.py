"""Schemat ideowy (jednokreskowy) rozdzielnicy głównej RG — matplotlib, symbole wg PN-EN 60617 (IEC 60617) w uproszczeniu:

* wyłącznik nadprądowy (S00287: zestyk z krzyżykiem), wyłącznik różnicowoprądowy / RCBO (zestyk + przekładnik
  sumujący — owal na torze), rozłącznik izolacyjny (zestyk z kreską poprzeczną), bezpiecznik (prostokąt z torem),
  licznik energii (prostokąt „Wh”), ogranicznik przepięć (prostokąt z warystorem → uziemienie), uziemienie (S00200),
  przycisk PWP z wyzwalaczem (prostokąt „PWP” + linia mechaniczna przerywana).

Wejście: :class:`lamela.obliczenia.elektryka.obwody.WynikObwody`. Symbole i legendę opisano na arkuszu (PN-EN 60617-11
wycofana bez następcy — symbole tylko z legendą, rejestr A.3).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Ellipse, Rectangle  # noqa: E402

from ..inst_wspolne import f  # noqa: E402

LW = 1.0


def _zestyk(ax, x, y, h=6.0, typ="wylacznik"):
    """Zestyk pionowy od y (góra) do y−h: linia doprowadzenia, ramię ukośne, element typu na styku stałym."""
    ax.plot([x, x], [y, y - h * 0.3], "k-", lw=LW)
    ax.plot([x, x + h * 0.25], [y - h * 0.3, y - h * 0.75], "k-", lw=LW)      # ramię
    ax.plot([x, x], [y - h * 0.7, y - h], "k-", lw=LW)
    s = h * 0.09
    yc = y - h * 0.3
    if typ == "wylacznik":
        ax.plot([x - s, x + s], [yc - s, yc + s], "k-", lw=LW)
        ax.plot([x - s, x + s], [yc + s, yc - s], "k-", lw=LW)
    elif typ == "rozlacznik":
        ax.plot([x - s * 1.3, x + s * 1.3], [yc, yc], "k-", lw=LW * 1.4)


def _rcd(ax, x, y, h):
    ax.add_patch(Ellipse((x, y), h * 0.35, h * 0.14, fill=False, lw=LW))
    ax.plot([x + h * 0.18, x + h * 0.45], [y, y], "k--", lw=0.6)


def _uziemienie(ax, x, y, s=2.0):
    ax.plot([x, x], [y, y - s * 0.6], "k-", lw=LW)
    for i, w in enumerate((1.0, 0.65, 0.3)):
        yy = y - s * 0.6 - i * s * 0.25
        ax.plot([x - s * w / 2, x + s * w / 2], [yy, yy], "k-", lw=LW)


def _spd(ax, x, y, label):
    ax.plot([x, x], [y, y - 3], "k-", lw=LW)
    ax.add_patch(Rectangle((x - 1.6, y - 8), 3.2, 5, fill=False, lw=LW))
    ax.plot([x - 1.2, x + 1.2], [y - 7.2, y - 3.8], "k-", lw=0.8)
    ax.plot([x + 1.2, x + 1.2 - 0.6], [y - 3.8, y - 3.8], "k-", lw=0.8)
    ax.plot([x, x], [y - 8, y - 10], "k-", lw=LW)
    _uziemienie(ax, x, y - 10)
    ax.text(x + 2.2, y - 5.5, label, fontsize=5.5, va="center")


LEGENDA_RG = ["× na zestyku — wyłącznik nadprądowy (B/C I_n)", "owal na torze — człon różnicowoprądowy 30 mA (typ A/F/B)",
              "kreska na zestyku — rozłącznik izolacyjny", "kreski na torze — liczba faz (1f / 3f)",
              "prostokąt ze skosem — SPD (warystor)"]


def rysuj_schemat_rg(wynik, plik, tytul: str | None = None, dpi: int = 200, legenda: bool = True) -> str:
    """Rysuje schemat jednokreskowy RG do pliku PNG; zwraca ścieżkę."""
    obw = wynik.obwody
    n = len(obw) + 2                      # + rezerwa
    dx = 11.0
    x0 = 100.0
    W = x0 + n * dx + 12
    H = 200.0
    fig_w = max(12.0, W / 25.4 * 0.95)
    fig, ax = plt.subplots(figsize=(fig_w, H / 25.4 * 0.95))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    yb = 160.0                            # szyna RG
    # --- ZKP
    ax.add_patch(Rectangle((4, 103), 42, 63, fill=False, lw=LW, ls="--"))
    ax.text(6, 168, "ZKP (ZK1x-1P) — własność OSD", fontsize=6.5, weight="bold")
    xz = 20
    ax.plot([xz, xz], [178, 158], "k-", lw=LW)
    ax.text(xz + 2, 176, "sieć nN 0,4 kV (TN-C)", fontsize=5.5)
    ax.add_patch(Rectangle((xz - 1.2, 152), 2.4, 6, fill=False, lw=LW))
    ax.plot([xz, xz], [152, 158], "k-", lw=0.6)
    ax.text(xz + 2.5, 155, "rozłącznik bezp. gG", fontsize=5.5, va="center")
    ax.plot([xz, xz], [152, 146], "k-", lw=LW)
    ax.add_patch(Rectangle((xz - 4, 138), 8, 8, fill=False, lw=LW))
    ax.text(xz, 142, "Wh", ha="center", va="center", fontsize=6)
    ax.text(xz + 5, 142, "licznik 3f\n(dwukierunkowy)", fontsize=5, va="center")
    ax.plot([xz, xz], [138, 134], "k-", lw=LW)
    _zestyk(ax, xz, 134, 8, "wylacznik")
    ax.text(xz + 3.5, 130, f"3P {wynik.par.zab_przedlicznikowe}40\n(przedlicznikowe)", fontsize=5.5, va="center")
    ax.plot([xz, xz], [126, 104], "k-", lw=LW)
    ax.text(xz + 1.5, 118, "PEN", fontsize=5.5)
    ax.plot([xz - 8, xz], [112, 112], "k-", lw=0.6)
    _uziemienie(ax, xz - 8, 112)
    # --- WLZ
    ax.plot([xz, xz, 58], [104, 100, 100], "k-", lw=LW * 1.6)
    ax.text(22, 88, f"WLZ {wynik.wlz['przewod']}, L = {f(wynik.wlz['L'], 1)} m\n∆U = {f(wynik.wlz['dU'], 2)} % (ziemia, D1)", fontsize=5.5)
    # --- RG
    ax.add_patch(Rectangle((54, 8), W - 58, 178, fill=False, lw=LW * 1.4))
    ax.text(56, 181, "RG — rozdzielnica główna (PN-EN IEC 61439-3), układ TN-S", fontsize=7, weight="bold")
    xr = 64
    ax.plot([58, xr, xr], [100, 100, 108], "k-", lw=LW * 1.6)
    _zestyk(ax, xr, 116, 8, "rozlacznik")
    ax.add_patch(Rectangle((xr + 4, 111), 7, 4, fill=False, lw=LW))
    ax.text(xr + 7.5, 113, "PWP", ha="center", va="center", fontsize=5.5)
    ax.plot([xr + 1.5, xr + 4], [113, 113], "k--", lw=0.6)
    ax.text(xr + 12, 113, "Q0: rozłącznik 3P 63 A\nz wyzwalaczem PWP", fontsize=5.5, va="center")
    ax.plot([xr, xr, x0 - 5], [116, yb, yb], "k-", lw=LW)
    _spd(ax, 80, yb, "SPD T1+T2\nI_imp ≥ 12,5 kA\nU_p ≤ 1,5 kV")
    ax.plot([58, W - 8], [14, 14], "g-", lw=1.2)
    ax.text(60, 15.5, "PE — szyna PE / GSU → uziom", fontsize=5.5, color="g")
    _uziemienie(ax, 58, 14)
    ax.plot([x0 - 5, x0 + n * dx], [yb, yb], "k-", lw=2.2)
    ax.text(x0 - 4, yb + 1.5, "L1 L2 L3 N", fontsize=5.5)
    for i, o in enumerate(obw + [None, None]):
        x = x0 + i * dx + dx / 2
        ax.plot([x, x], [yb, yb - 4], "k-", lw=LW)
        _zestyk(ax, x, yb - 4, 10, "wylacznik")
        if o is None:
            ax.plot([x, x], [yb - 14, yb - 58], "k:", lw=0.6)
            ax.text(x, yb - 60, "rezerwa", rotation=90, fontsize=5.5, ha="center", va="top")
            continue
        rc = o.odb.rcd
        if "RC" in rc:
            _rcd(ax, x, yb - 9.5, 10)
        lab = f"{o.zab}"
        if "30 mA" in rc:
            typ = "B" if "typ B" in rc else ("F" if "typ F" in rc else "A")
            lab += f"\n30mA {typ}"
        ax.text(x - 0.5, yb - 16, lab, fontsize=4.8, ha="right", va="top", rotation=90)
        ax.plot([x, x], [yb - 14, yb - 58], "k-", lw=LW)
        nf = 3 if o.odb.fazy == 3 else 1
        for k in range(nf):
            dxk = (k - (nf - 1) / 2) * 0.6
            ax.plot([x - 0.9 + dxk, x + 0.9 + dxk], [yb - 42 - 0.9, yb - 42 + 0.9], "k-", lw=0.6)
        ax.text(x + 0.9, yb - 16, f"{o.przewod}  L={f(o.L, 0)} m", fontsize=4.6, rotation=90, va="top")
        ax.text(x + 0.9, yb - 45, f"∆U={f(o.dU_calk, 1)}%", fontsize=4.4, rotation=90, va="top")
        ax.text(x, yb - 60, o.odb.id, fontsize=5.4, ha="center", va="top", weight="bold")
        ax.text(x, yb - 64.5, o.odb.faza.replace("L1L2L3", "3f"), fontsize=4.8, ha="center", va="top")
        # pełna nazwa odbiorów: do szyny PE mieści się ok. 70 znaków; dłuższa — 2 wiersze (pas obwodu 11 mm),
        # bez ucinania „…” (weryfikacja arkuszy C 2.4)
        import textwrap
        ls = textwrap.wrap(o.odb.nazwa, 68, break_long_words=False) or [""]
        if len(ls) > 2:                   # lista pomieszczeń dłuższa niż 2 wiersze — odesłanie do tabeli obwodów
            dop = " i in. (wg tabeli obwodów)"
            ls = [ls[0], textwrap.shorten(" ".join(ls[1:]), 68 - len(dop), placeholder="").rstrip(",;") + dop]
        ax.text(x, yb - 69, "\n".join(ls), fontsize=4.6, rotation=90, ha="center", va="top", linespacing=1.05)
    if legenda:                          # arkusz rysunkowy: legenda w bloku OZNACZENIA kolumny opisowej
        lx, ly = W - 74, 178
        ax.text(lx, ly, "Legenda (PN-EN 60617, uproszczone):", fontsize=5.5, weight="bold")
        for i, t in enumerate(LEGENDA_RG):
            ax.text(lx, ly - 3.2 * (i + 1), t, fontsize=5)
    ax.text(56, 3, tytul or f"Schemat ideowy RG — {wynik.dane.nazwa}. Dane przykładowe [ZAŁ]; wartości z obliczeń obwodów "
            "(lamela.obliczenia.elektryka.obwody).", fontsize=6)
    fig.savefig(plik, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(plik)
