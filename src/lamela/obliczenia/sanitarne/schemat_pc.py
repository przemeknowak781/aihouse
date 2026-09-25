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
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 270)
    ax.set_ylim(0, 170)
    ax.set_aspect("equal")
    ax.axis("off")
    YS, YR = 128.0, 108.0                     # zasilanie / powrót c.o.
    # --- jednostka zewnętrzna
    ax.add_patch(Rectangle((4, 100), 26, 34, fc="#eeeeee", ec="k", lw=1.2))
    ax.add_patch(Circle((17, 120), 9, fill=False, ec="k"))
    ax.plot([17, 17], [111, 129], "k-", lw=0.6)
    ax.plot([8, 26], [120, 120], "k-", lw=0.6)
    ax.text(17, 103, "PC R290 — monoblok", ha="center", fontsize=6)
    ax.text(4, 138, f"{pc['model']}\nP(A−7/W35) = {f(pc['P'][1], 1)} kW; SCOP {f(pc['SCOP_35'], 1)}\n"
                    f"L_WA {f(pc['L_WA'], 0)} dB(A); θ_biv = {f(og.biwalentny['theta_biv'], 1)} °C", fontsize=5.5)
    ax.plot([36, 36], [92, 150], "k--", lw=0.8)
    ax.text(37, 150, "ściana zewnętrzna", fontsize=5, rotation=90, va="top")
    _linia(ax, [(30, YS), (72, YS)], CZ)
    _linia(ax, [(30, YR), (70, YR)], NB)
    ax.text(38, YS - 6, f"{og.przewody_pc['rura']}; na zewnątrz izolacja ≥ {f(og.przewody_pc['izol_zewn'], 0)} mm", fontsize=5)
    _zawor(ax, 42, YS, c=CZ)
    _zawor(ax, 42, YR, c=NB)
    ax.text(42, YR - 7, "zawory\nantyzamarz.", fontsize=4.5, ha="center")
    _zb(ax, 56, YS, f"ZB {f(og.par.p_SV, 1)} bar")
    _zawor3(ax, 76, YS)
    ax.text(80, YS + 3, "ZP3D c.o./c.w.u.", fontsize=5)
    _linia(ax, [(72, YS), (74, YS)], CZ)
    # zasobnik
    ax.add_patch(FancyBboxPatch((92, 14), 26, 60, boxstyle="round,pad=0.5,rounding_size=6", fc="white", ec="k", lw=1.2))
    ax.text(105, 66, f"zasobnik c.w.u.\n{f(woda.cwu['V_zas'], 0)} dm³", ha="center", fontsize=6, weight="bold")
    ax.text(105, 56, f"wężownica ≥ {f(woda.cwu['A_wez'], 1)} m²", ha="center", fontsize=5)
    _linia(ax, [(76, YS - 4), (76, 50), (96, 50)], CZ)
    xs = [96 + (i % 2) * 18 for i in range(8)]
    ys = [50 - i * 3.0 for i in range(8)]
    _linia(ax, list(zip(xs, ys)), CZ, lw=1.0)
    _linia(ax, [(114, 29), (96, 29), (84, 29), (84, 100), (66, 100), (66, YR)], NB)
    ax.plot([118, 123], [22, 22], "k-", lw=1.2)
    ax.add_patch(Rectangle((123, 20), 5, 4, fc="white", ec="k"))
    ax.text(129, 22, f"grzałka el. — dezynfekcja {f(og.par.theta_dez, 0)} °C\n(WT §120 ust. 2a)", fontsize=5, va="center")
    # bufor, pompa, naczynie c.o. (powrót)
    ax.add_patch(FancyBboxPatch((52, 96), 10, 24, boxstyle="round,pad=0.4,rounding_size=4", fc="white", ec="k", zorder=3))
    ax.text(57, 108, f"bufor\n{og.bufor['V_dob']}\ndm³", ha="center", va="center", fontsize=5, zorder=4)
    _pompa(ax, 46, YR, kier=-1)
    ax.text(46, YR + 3, f"pompa\nH ≈ {f(og.przewody_pc['H_pompy_kPa'], 0)} kPa", ha="center", fontsize=4.8, va="bottom")
    ax.plot([48, 48], [YR, YR - 12], "k-", lw=0.8)
    _naczynie(ax, 48, YR - 12, f"NW c.o. {og.naczynie_co['V_dob']} dm³, p₀ = {f(og.naczynie_co['p_0'], 1)} bar")
    # c.o. → rozdzielacze
    _linia(ax, [(80, YS), (150, YS)], CZ)
    _linia(ax, [(150, YR), (70, YR)], NB)
    for i, r in enumerate(og.rozdzielacze[:2]):
        x = 150 + i * 58
        ax.add_patch(Rectangle((x, 134), 44, 3.5, fc=CZ, ec="k", alpha=0.3))
        ax.add_patch(Rectangle((x, 140), 44, 3.5, fc=NB, ec="k", alpha=0.3))
        _linia(ax, [(150, YS), (x + 1, YS), (x + 1, 134)], CZ, lw=1.2)
        _linia(ax, [(x + 43, 140), (x + 46, 140), (x + 46, YR), (150, YR)], NB, lw=1.2)
        for k in range(min(r["petle"], 9)):
            xx = x + 3 + k * 4.6
            _linia(ax, [(xx, 137.5), (xx, 160), (xx + 2.2, 160), (xx + 2.2, 143.5)], "#7f8c8d", lw=0.6)
        ax.text(x + 22, 163, f"rozdzielacz {r['kond']}: {r['petle']} pętli, Σṁ = {f(r['m_kgh'], 0)} kg/h", ha="center", fontsize=5)
    ax.text(150, 118, f"Ogrzewanie podłogowe (PN-EN 1264): θ_V,des = {f(og.theta_V, 1)} °C, PE-X 16×2,\n"
                      f"pętle ≤ {f(og.par.L_petli_max, 0)} m; siłowniki + termostaty pokojowe (WT §135 ust. 7)", fontsize=5.5)
    # woda zimna
    yz = 6
    _linia(ax, [(4, yz), (140, yz)], ZW)
    for x0, t in ((10, "WM"), (29, "EA"), (40, "RED")):
        ax.add_patch(Rectangle((x0, yz - 3), 7, 6, fc="white", ec="k", zorder=3))
        ax.text(x0 + 3.5, yz, t, ha="center", va="center", fontsize=4.5, zorder=4)
    _zawor(ax, 23, yz, c=ZW)
    ax.text(23, yz + 3, "F", ha="center", fontsize=5)
    ax.text(4, yz + 11, f"woda zimna z przyłącza: wodomierz {woda.do_dict()['wodomierz']}, filtr, EA (PN-EN 1717), reduktor", fontsize=5)
    _linia(ax, [(98, yz), (98, 14)], ZW)
    ax.add_patch(Rectangle((84, yz + 2), 6, 5, fc="white", ec="k"))
    ax.text(87, yz + 4.5, "GB", ha="center", va="center", fontsize=4.5)
    ax.text(84, 15, "grupa bezp.\n6 bar + EA", fontsize=4.5, ha="right")
    ax.plot([70, 70], [yz, yz + 4], "k-", lw=0.8)
    _naczynie(ax, 70, yz + 12, "")
    ax.text(66, 14, f"NW c.w.u.\n{og.naczynie_cwu['V_dob']} dm³", fontsize=5, ha="right", va="center")
    # c.w.u. → TZM → punkty
    _linia(ax, [(112, 74), (112, 84), (132, 84)], CW)
    ax.add_patch(Polygon([(132, 81), (132, 87), (138, 84)], closed=True, fc="white", ec="k"))
    ax.add_patch(Polygon([(144, 81), (144, 87), (138, 84)], closed=True, fc="white", ec="k"))
    ax.text(138, 89, "TZM", ha="center", fontsize=5)
    _linia(ax, [(140, yz), (140, 60), (138, 60), (138, 81)], ZW, lw=1.0)
    _linia(ax, [(144, 84), (185, 84)], CW)
    ax.text(150, 86, f"c.w.u. do punktów 55–60 °C (WT §120 ust. 2); V_d = {f(woda.cwu['V_d'], 0)} dm³/d", fontsize=5)
    if woda.cwu["cyrkulacja"] != "brak":
        _linia(ax, [(185, 76), (124, 76), (124, 40), (118.5, 40)], CY, lw=1.0, ls="--")
        _pompa(ax, 124, 58, r=1.8, kier=1)
        ax.text(127, 58, f"cyrkulacja czasowa {f(woda.cwu['V_cyrk_dm3h'], 0)} dm³/h, {f(woda.cwu['h_cyrk'], 0)} h/d;\n"
                         f"η_W,d = {f(woda.cwu['eta_W_d'], 2)} (metodologia EP)", fontsize=4.8, va="center")
    # legenda
    lx, ly = 200, 64
    ax.text(lx, ly, "Legenda:", fontsize=6, weight="bold")
    for i, (c, t) in enumerate(((CZ, "zasilanie c.o. / wężownicy"), (NB, "powrót c.o."), (ZW, "woda zimna"), (CW, "c.w.u."),
                                 (CY, "cyrkulacja"))):
        ax.plot([lx, lx + 8], [ly - 5 - i * 4, ly - 5 - i * 4], color=c, lw=1.6, ls="--" if c == CY else "-")
        ax.text(lx + 10, ly - 5 - i * 4, t, fontsize=5, va="center")
    oth = ["koło z trójkątem — pompa", "kokarda — zawór odcinający / antyzamarzaniowy", "ZP3D — zawór przełączający 3-drogowy",
           "NW — naczynie wzbiorcze przeponowe", "ZB — zawór bezpieczeństwa; GB — grupa bezpieczeństwa",
           "TZM — termostatyczny zawór mieszający", "WM — wodomierz; F — filtr; EA — zawór antyskażeniowy; RED — reduktor"]
    for i, t in enumerate(oth):
        ax.text(lx, ly - 27 - i * 3.6, t, fontsize=5)
    ax.text(2, -4, "Schemat ideowy PC / c.w.u. — dane przykładowe [ZAŁ]; wartości z modułów lamela.obliczenia.sanitarne "
                   "(ogrzewanie, woda).", fontsize=6)
    ax.set_ylim(-6, 170)
    fig.savefig(plik, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return str(plik)
