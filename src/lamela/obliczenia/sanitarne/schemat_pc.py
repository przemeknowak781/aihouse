"""Schemat ideowy źródła ciepła i c.w.u.: monoblok powietrze–woda (R290) → zawór przełączający c.o./c.w.u. → zasobnik
c.w.u. z wężownicą (grzałka, dezynfekcja) / rozdzielacze ogrzewania podłogowego → bufor szeregowy na powrocie → pompa;
naczynie wzbiorcze c.o. i c.w.u., zawory bezpieczeństwa, zestaw wodomierzowy (EA), termostatyczny zawór mieszający,
cyrkulacja czasowa. Symbole umowne (PN-EN ISO 10628 / praktyka; PN-B-01410 wycofana) — z legendą. matplotlib.

Wejście: wyniki :func:`ogrzewanie.oblicz_ogrzewanie` i :func:`woda.oblicz_wode` (wartości opisane na schemacie).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle  # noqa: E402

from ..inst_wspolne import f  # noqa: E402

CZ, NB, ZW, CW, CY = "#c0392b", "#2e6db4", "#2e8b57", "#d35400", "#8e44ad"


def _linia(ax, pts, c, lw=1.6, ls="-"):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=lw, ls=ls, solid_capstyle="butt")


def _pompa(ax, x, y, r=2.2, kier=1):
    ax.add_patch(Circle((x, y), r, fill=True, fc="white", ec="k", lw=1))
    ax.add_patch(Polygon([(x - r * 0.6 * kier, y + r * 0.6), (x - r * 0.6 * kier, y - r * 0.6), (x + r * 0.8 * kier, y)],
                         closed=True, fc="k"))


def _zawor(ax, x, y, s=1.8, pion=False, c="k"):
    if pion:
        ax.add_patch(Polygon([(x - s, y + s), (x + s, y + s), (x - s, y - s), (x + s, y - s)], closed=True, fc="white", ec=c, lw=1))
    else:
        ax.add_patch(Polygon([(x - s, y - s), (x - s, y + s), (x + s, y - s), (x + s, y + s)], closed=True, fc="white", ec=c, lw=1))


def _zawor3(ax, x, y, s=2.0):
    ax.add_patch(Polygon([(x - s, y - s), (x - s, y + s), (x, y)], closed=True, fc="white", ec="k"))
    ax.add_patch(Polygon([(x + s, y - s), (x + s, y + s), (x, y)], closed=True, fc="white", ec="k"))
    ax.add_patch(Polygon([(x - s, y - 2 * s), (x + s, y - 2 * s), (x, y)], closed=True, fc="k", ec="k"))


def _naczynie(ax, x, y, label):
    ax.add_patch(FancyBboxPatch((x - 3, y - 8), 6, 8, boxstyle="round,pad=0.4,rounding_size=2.5", fc="#f2f2f2", ec="k"))
    ax.text(x, y - 4, "NW", ha="center", va="center", fontsize=5)
    ax.text(x + 4, y - 4, label, fontsize=5, va="center")


def _zb(ax, x, y, label):
    ax.add_patch(Polygon([(x - 1.5, y), (x + 1.5, y), (x, y + 2.5)], closed=True, fc="white", ec="k"))
    ax.plot([x, x + 2], [y + 2.5, y + 4.5], "k-", lw=0.8)
    ax.text(x + 2.5, y + 4.5, label, fontsize=5)


def rysuj_schemat_pc(og, woda, plik, dpi: int = 200) -> str:
    pc = og.pc
    fig, ax = plt.subplots(figsize=(16, 9.5))
    ax.set_xlim(0, 270)
    ax.set_ylim(0, 160)
    ax.set_aspect("equal")
    ax.axis("off")
    # --- jednostka zewnętrzna
    ax.add_patch(Rectangle((4, 70), 26, 34, fc="#eeeeee", ec="k", lw=1.2))
    ax.add_patch(Circle((17, 90), 9, fill=False, ec="k"))
    ax.plot([17, 17], [81, 99], "k-", lw=0.6)
    ax.plot([8, 26], [90, 90], "k-", lw=0.6)
    ax.text(17, 74, "PC R290\nmonoblok", ha="center", fontsize=6)
    ax.text(4, 108, f"{pc['model']}\nP(A−7/W35) = {f(pc['P'][1], 1)} kW; SCOP {f(pc['SCOP_35'], 1)}\n"
                    f"L_WA {f(pc['L_WA'], 0)} dB(A); θ_biv = {f(og.biwalentny['theta_biv'], 1)} °C", fontsize=5.5)
    ax.plot([34, 34], [60, 115], "k--", lw=0.8)
    ax.text(35, 116, "ściana zewnętrzna", fontsize=5, rotation=90, va="bottom")
    # zasilanie / powrót PC
    _linia(ax, [(30, 98), (70, 98)], CZ)
    _linia(ax, [(30, 78), (70, 78)], NB)
    ax.text(38, 100, f"{og.przewody_pc['rura']}, izolacja zewn. ≥ {f(og.przewody_pc['izol_zewn'], 0)} mm", fontsize=5)
    _zawor(ax, 40, 98, c=CZ)
    _zawor(ax, 40, 78, c=NB)
    ax.text(40, 92, "zawory\nantyzamarz.", fontsize=4.5, ha="center")
    # zawór 3-drogowy
    _zawor3(ax, 74, 98)
    ax.text(74, 104, "ZP3D c.o./c.w.u.", fontsize=5, ha="center")
    _linia(ax, [(70, 98), (72, 98)], CZ)
    # do zasobnika (wężownica)
    _linia(ax, [(74, 94), (74, 60), (92, 60)], CZ)
    # zasobnik
    ax.add_patch(FancyBboxPatch((92, 30), 26, 66, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec="k", lw=1.2))
    xs = [96 + (i % 2) * 18 for i in range(8)]
    ys = [60 - i * 3.3 for i in range(8)]
    _linia(ax, list(zip(xs, ys)), CZ, lw=1.0)
    _linia(ax, [(92, 36), (70, 36), (70, 74)], NB)
    ax.text(105, 88, f"zasobnik c.w.u.\n{f(woda.cwu['V_zas'], 0)} dm³", ha="center", fontsize=6, weight="bold")
    ax.text(105, 70, f"wężownica ≥ {f(woda.cwu['A_wez'], 1)} m²", ha="center", fontsize=5)
    ax.plot([118, 124], [48, 48], "k-", lw=1.2)
    ax.add_patch(Rectangle((124, 46), 5, 4, fc="white", ec="k"))
    ax.text(130, 48, "grzałka el. (dezynfekcja\n" + f"{f(og.par.theta_dez, 0)} °C, WT §120 ust. 2a)", fontsize=5, va="center")
    # c.o. — do bufora / rozdzielaczy
    _linia(ax, [(78, 98), (150, 98)], CZ)
    _linia(ax, [(150, 78), (70, 78)], NB)
    # bufor szeregowy na powrocie
    ax.add_patch(FancyBboxPatch((52, 66), 12, 24, boxstyle="round,pad=0.4,rounding_size=4", fc="white", ec="k"))
    ax.text(58, 78, f"bufor\n{og.bufor['V_dob']} dm³", ha="center", va="center", fontsize=5)
    _pompa(ax, 46, 78, kier=-1)
    ax.text(46, 72, f"pompa\nH ≈ {f(og.przewody_pc['H_pompy_kPa'], 0)} kPa", ha="center", fontsize=4.8, va="top")
    _naczynie(ax, 48, 64, f"c.o. {og.naczynie_co['V_dob']} dm³\np0 = {f(og.naczynie_co['p_0'], 1)} bar")
    ax.plot([48, 48], [64, 78], "k-", lw=0.8)
    _zb(ax, 64, 98, f"ZB {f(og.par.p_SV, 1)} bar")
    # rozdzielacze
    ym = 120
    for i, r in enumerate(og.rozdzielacze):
        x = 150 + i * 55
        ax.add_patch(Rectangle((x, 104 + 0), 40, 4, fc=CZ, ec="k", alpha=0.25))
        ax.add_patch(Rectangle((x, 96 - 20), 40, 4, fc=NB, ec="k", alpha=0.25))
        _linia(ax, [(150, 98), (x, 98), (x, 106)], CZ, lw=1.2)
        _linia(ax, [(150, 78), (x, 78)], NB, lw=1.2)
        for k in range(min(r["petle"], 8)):
            xx = x + 3 + k * 4.7
            _linia(ax, [(xx, 108), (xx, 140), (xx + 2, 140), (xx + 2, 80)], "#7f8c8d", lw=0.6)
        ax.text(x + 20, 143, f"rozdzielacz {r['kond']}: {r['petle']} pętli\nΣṁ = {f(r['m_kgh'], 0)} kg/h; siłowniki + termostaty",
                ha="center", fontsize=5)
    ax.text(150, 150, f"Ogrzewanie podłogowe (PN-EN 1264): θ_V,des = {f(og.theta_V, 1)} °C; PE-X 16×2; pętle ≤ {f(og.par.L_petli_max, 0)} m",
            fontsize=6, weight="bold")
    # c.w.u.
    yz = 14
    _linia(ax, [(4, yz), (92, yz)], ZW)
    ax.add_patch(Rectangle((10, yz - 3), 8, 6, fc="white", ec="k"))
    ax.text(14, yz, "WM", ha="center", va="center", fontsize=5)
    _zawor(ax, 24, yz, c=ZW)
    ax.text(24, yz + 3, "F", ha="center", fontsize=5)
    ax.add_patch(Rectangle((29, yz - 3), 7, 6, fc="white", ec="k"))
    ax.text(32.5, yz, "EA", ha="center", va="center", fontsize=5)
    ax.add_patch(Rectangle((40, yz - 3), 7, 6, fc="white", ec="k"))
    ax.text(43.5, yz, "RED", ha="center", va="center", fontsize=4.5)
    ax.text(4, yz - 7, f"woda zimna z przyłącza — zestaw wodomierzowy: wodomierz {woda.do_dict()['wodomierz']}, filtr, EA (PN-EN 1717), "
                       "reduktor", fontsize=5)
    _linia(ax, [(92, yz), (98, yz), (98, 30)], ZW)
    ax.add_patch(Rectangle((80, yz + 2), 6, 5, fc="white", ec="k"))
    ax.text(83, yz + 4.5, "GB", ha="center", va="center", fontsize=4.5)
    ax.text(80, yz + 9, "grupa bezp.\n6 bar + EA", fontsize=4.5)
    _naczynie(ax, 72, yz + 12, f"c.w.u. {og.naczynie_cwu['V_dob']} dm³")
    ax.plot([72, 72], [yz + 4, yz], "k-", lw=0.8)
    # wyjście c.w.u. → TZM → punkty
    _linia(ax, [(112, 96), (112, 124), (130, 124)], CW)
    ax.add_patch(Polygon([(130, 121), (130, 127), (136, 124)], closed=True, fc="white", ec="k"))
    ax.add_patch(Polygon([(142, 121), (142, 127), (136, 124)], closed=True, fc="white", ec="k"))
    ax.text(136, 129, "TZM", ha="center", fontsize=5)
    _linia(ax, [(136, yz), (136, 121)], ZW, lw=1.0)
    _linia(ax, [(92 + 50, yz), (136, yz)], ZW, lw=1.0)
    _linia(ax, [(142, 124), (146, 124), (146, 132), (140, 132), (122, 132)], CW)
    ax.text(100, 134, f"c.w.u. do punktów 55–60 °C (WT §120 ust. 2); V_d = {f(woda.cwu['V_d'], 0)} dm³/d", fontsize=5)
    if woda.cwu["cyrkulacja"] != "brak":
        _linia(ax, [(122, 128), (116, 128), (116, 80), (118, 80)], CY, lw=1.0, ls="--")
        _pompa(ax, 116, 110, r=1.8, kier=1)
        ax.text(98, 104, f"cyrkulacja czasowa\n{f(woda.cwu['V_cyrk_dm3h'], 0)} dm³/h, {f(woda.cwu['h_cyrk'], 0)} h/d\n"
                         f"η_W,d = {f(woda.cwu['eta_W_d'], 2)}", fontsize=4.8)
    # legenda
    lx, ly = 190, 56
    ax.text(lx, ly, "Legenda:", fontsize=6, weight="bold")
    for i, (c, t) in enumerate(((CZ, "zasilanie c.o. / wężownicy"), (NB, "powrót"), (ZW, "woda zimna"), (CW, "c.w.u."),
                                 (CY, "cyrkulacja"))):
        ax.plot([lx, lx + 8], [ly - 5 - i * 4, ly - 5 - i * 4], color=c, lw=1.6, ls="--" if c == CY else "-")
        ax.text(lx + 10, ly - 5 - i * 4, t, fontsize=5, va="center")
    oth = ["koło z trójkątem — pompa obiegowa", "kokarda — zawór odcinający", "ZP3D — zawór przełączający 3-drogowy",
           "NW — naczynie wzbiorcze przeponowe", "ZB — zawór bezpieczeństwa", "TZM — termostatyczny zawór mieszający",
           "WM — wodomierz; F — filtr; EA — zawór antyskażeniowy; RED — reduktor"]
    for i, t in enumerate(oth):
        ax.text(lx, ly - 27 - i * 3.6, t, fontsize=5)
    ax.text(2, 2, "Schemat ideowy PC / c.w.u. — dane przykładowe [ZAŁ]; wartości z modułów lamela.obliczenia.sanitarne "
                  "(ogrzewanie, woda).", fontsize=6)
    fig.savefig(plik, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(plik)
