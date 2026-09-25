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


def rysuj_schemat_rg(wynik, plik, tytul: str | None = None, dpi: int = 200) -> str:
    """Rysuje schemat jednokreskowy RG do pliku PNG; zwraca ścieżkę."""
    obw = wynik.obwody
    n = len(obw) + 2                      # + rezerwa
    dx = 11.0
    x0 = 95.0
    W = x0 + n * dx + 20
    H = 150.0
    fig_w = max(12.0, W / 25.4 * 0.95)
    fig, ax = plt.subplots(figsize=(fig_w, H / 25.4 * 1.05))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    yb = 118.0                            # szyna RG
    # --- ZKP
    ax.add_patch(Rectangle((4, 70), 36, 62, fill=False, lw=LW, ls="--"))
    ax.text(22, 129.5, "ZKP (ZK1x-1P) — OSD", ha="center", fontsize=6.5, weight="bold")
    xz = 22
    ax.plot([xz, xz], [136, 126], "k-", lw=LW)
    ax.text(xz + 2, 134, "sieć nN 0,4 kV TN-C", fontsize=5.5)
    ax.add_patch(Rectangle((xz - 1.2, 120), 2.4, 6, fill=False, lw=LW))      # bezpiecznik/rozłącznik bezp.
    ax.plot([xz, xz], [120, 126], "k-", lw=0.6)
    ax.text(xz + 2, 122.5, "rozł. bezp. gG", fontsize=5.5)
    ax.plot([xz, xz], [120, 114], "k-", lw=LW)
    ax.add_patch(Rectangle((xz - 4, 106), 8, 8, fill=False, lw=LW))
    ax.text(xz, 110, "Wh", ha="center", va="center", fontsize=6)
    ax.text(xz + 5, 110, "licznik 3f\n(dwukierunkowy)", fontsize=5, va="center")
    ax.plot([xz, xz], [106, 102], "k-", lw=LW)
    _zestyk(ax, xz, 102, 8, "wylacznik")
    ax.text(xz + 3.5, 98, f"3P {wynik.par.zab_przedlicznikowe}40\n(przedlicznikowe)", fontsize=5.5, va="center")
    ax.plot([xz, xz], [94, 76], "k-", lw=LW)
    ax.text(xz + 1.5, 86, "PEN", fontsize=5.5)
    _uziemienie(ax, xz - 8, 80)
    ax.plot([xz - 8, xz], [80, 80], "k-", lw=0.6)
    # --- WLZ
    ax.plot([xz, xz, 55], [76, 72, 72], "k-", lw=LW * 1.6)
    ax.text(38, 73.5, f"WLZ {wynik.wlz['przewod']}\nL = {f(wynik.wlz['L'], 1)} m, ∆U = {f(wynik.wlz['dU'], 2)} %", fontsize=5.5)
    # --- RG
    ax.add_patch(Rectangle((50, 8), W - 55, 130, fill=False, lw=LW * 1.4))
    ax.text(52, 134.5, "RG — rozdzielnica główna (PN-EN IEC 61439-3), TN-S", fontsize=7, weight="bold")
    xr = 60
    ax.plot([55, xr, xr], [72, 72, 80], "k-", lw=LW * 1.6)
    _zestyk(ax, xr, 88, 8, "rozlacznik")
    ax.plot([xr, xr], [80, 80], "k-")
    ax.add_patch(Rectangle((xr + 4, 83), 7, 4, fill=False, lw=LW))
    ax.text(xr + 7.5, 85, "PWP", ha="center", va="center", fontsize=5.5)
    ax.plot([xr + 1.5, xr + 4], [85, 85], "k--", lw=0.6)
    ax.text(xr - 1, 92, "Q0: rozłącznik 3P 63 A\nz wyzwalaczem (PWP)", fontsize=5.5, ha="right")
    ax.plot([xr, xr, x0 - 5], [88, yb, yb], "k-", lw=LW)
    _spd(ax, 75, yb, "SPD T1+T2\nI_imp ≥ 12,5 kA\nU_p ≤ 1,5 kV")
    ax.plot([75, 75], [yb, yb], "k-")
    # szyny PE / N
    ax.plot([55, W - 8], [14, 14], "g-", lw=1.2)
    ax.text(56, 15.5, "PE (GSU, uziom)", fontsize=5.5, color="g")
    _uziemienie(ax, 56, 14)
    # szyna główna
    ax.plot([x0 - 5, x0 + n * dx], [yb, yb], "k-", lw=2.2)
    ax.text(x0 - 4, yb + 1.5, "L1 L2 L3 N", fontsize=5.5)
    for i, o in enumerate(obw + [None, None]):
        x = x0 + i * dx + dx / 2
        ax.plot([x, x], [yb, yb - 4], "k-", lw=LW)
        if o is None:
            _zestyk(ax, x, yb - 4, 10, "wylacznik")
            ax.plot([x, x], [yb - 14, yb - 50], "k:", lw=0.6)
            ax.text(x, yb - 52, "rezerwa", rotation=90, fontsize=5.5, ha="center", va="top")
            continue
        _zestyk(ax, x, yb - 4, 10, "wylacznik")
        rc = o.odb.rcd
        if "RC" in rc:
            _rcd(ax, x, yb - 9.5, 10)
        lab = f"{o.zab}"
        if "30 mA" in rc:
            typ = "B" if "typ B" in rc else ("F" if "typ F" in rc else "A")
            lab += f"\n30mA {typ}"
        ax.text(x - 0.5, yb - 16, lab, fontsize=4.8, ha="right", va="top", rotation=90)
        ax.plot([x, x], [yb - 14, yb - 58], "k-", lw=LW)
        if o.odb.fazy == 3:
            for k in (-1, 0, 1):
                ax.plot([x - 0.9 + k * 0.5, x + 0.9 + k * 0.5], [yb - 40 - 0.9, yb - 40 + 0.9], "k-", lw=0.6)
        else:
            ax.plot([x - 0.9, x + 0.9], [yb - 40 - 0.9, yb - 40 + 0.9], "k-", lw=0.6)
        ax.text(x + 0.9, yb - 20, f"{o.przewod}  L={f(o.L, 0)} m", fontsize=4.6, rotation=90, va="top")
        ax.text(x + 0.9, yb - 45, f"∆U={f(o.dU_calk, 1)}%", fontsize=4.4, rotation=90, va="top")
        ax.text(x, yb - 60, f"{o.odb.id}  {o.odb.faza}", fontsize=5.2, ha="center", va="top", weight="bold")
        ax.text(x, yb - 64, o.odb.nazwa[:52], fontsize=4.6, rotation=90, ha="center", va="top")
    # legenda
    lx, ly = W - 60, 132
    ax.text(lx, ly, "Legenda (PN-EN 60617, uproszczone):", fontsize=5.5, weight="bold")
    items = ["⨯ na zestyku — wyłącznik nadprądowy (B/C, I_n)", "owal na torze — człon różnicowoprądowy (RCBO/RCD 30 mA, typ)",
             "kreska na zestyku — rozłącznik izolacyjny", "/ , /// na torze — liczba faz (1f / 3f)", "prostokąt ze skosem — SPD"]
    for i, t in enumerate(items):
        ax.text(lx, ly - 3.5 * (i + 1), t, fontsize=5)
    ax.text(52, 3, tytul or f"Schemat ideowy RG — {wynik.dane.nazwa}. Dane przykładowe [ZAŁ]; wartości z obliczeń obwodów "
            "(lamela.obliczenia.elektryka.obwody).", fontsize=6)
    fig.savefig(plik, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(plik)
