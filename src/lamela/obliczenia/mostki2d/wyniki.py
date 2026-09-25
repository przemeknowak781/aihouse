"""Wyniki symulacji węzła: L_2D, ψ (wymiary zewnętrzne i wewnętrzne), θ_si,min i f_Rsi, wykresy, raport Markdown.

Procedura dla węzła (PN-EN ISO 10211:2017):
1. przebieg „ψ” — R_si wg ISO 6946 (0,13 / 0,10 / 0,17 wg kierunku strumienia), R_se = 0,04; siatka n i 2n
   (kryterium: zmiana całkowitego strumienia < 1 % przy podwojeniu liczby podziałów; w razie potrzeby 4n);
2. współczynniki sprzężenia L_2D między grupami stref (superpozycja rozwiązań jednostkowych; dla 2 temperatur
   L_2D = Φ/(θ_i − θ_e));
3. ψ = L_2D − Σ U_j·l_j — osobno dla wymiarów zewnętrznych (l_e) i wewnętrznych (l_i) (PN-EN ISO 14683 — systemy wymiarów);
4. przebieg „f_Rsi” — R_si = 0,25 (0,13 ramy/szyby) wg PN-EN ISO 13788 / PN-EN ISO 10211:
   f_Rsi = (θ_si,min − θ_e)/(θ_i − θ_e); ocena f_Rsi ≥ f_Rsi,min (W-248: 0,72 — WT zał. 2 pkt 2.2);
   dla 3 temperatur — współczynniki wagowe g (θ_si = Σ g_k·θ_k);
5. informacyjnie: θ_si przy θ_e obl. vs temperatura krytyczna pleśni (φ_si = 80 %) i punkt rosy przy φ_i = 50 %.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .geometria import PSI_DOMYSLNE_14683, Wezel
from .siatka import Siatka, siatka_dla_wezla
from .solver import ModelMOS, Rozwiazanie

KRYT_ZBIEZNOSCI = 0.01        # 1 % (ISO 10211 — podwojenie liczby podziałów)
KRYT_BILANSU = 1e-4
MAX_KOMOREK = 3_000_000


# --------------------------------------------------------------------------------------------------
# Formatowanie
# --------------------------------------------------------------------------------------------------
def fmt_liczba(x: Any, n: int = 3, znak: bool = False) -> str:
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(v):
        return "—"
    s = f"{v:+.{n}f}" if znak else f"{v:.{n}f}"
    if s in ("-0." + "0" * n, "+0." + "0" * n) and not znak:
        s = s.lstrip("-+")
    return s.replace(".", ",").replace("-", "−")


f_ = fmt_liczba


def _wym(klucz: str, sekcja: str, domyslna: float) -> tuple[float, str]:
    try:
        from ..wspolne import wymaganie
        w = wymaganie(sekcja, klucz, domyslna)
        return float(w.wartosc), w.opis()
    except Exception:   # pragma: no cover
        return domyslna, "wartość domyślna"


# --------------------------------------------------------------------------------------------------
# Wilgotność (PN-EN ISO 13788 zał. E — ciśnienie nasycenia)
# --------------------------------------------------------------------------------------------------
def p_sat(theta: float) -> float:
    if theta >= 0:
        return 610.5 * math.exp(17.269 * theta / (237.3 + theta))
    return 610.5 * math.exp(21.875 * theta / (265.5 + theta))


def theta_z_psat(p: float) -> float:
    r = math.log(p / 610.5)
    th = 237.3 * r / (17.269 - r)
    if th < 0:
        th = 265.5 * r / (21.875 - r)
    return th


def theta_krytyczne(theta_i: float, phi_i: float = 0.5, phi_si_max: float = 0.8) -> tuple[float, float]:
    """(θ_si,min dla φ_si ≤ 80 % — pleśń; punkt rosy) przy θ_i i φ_i."""
    pi = phi_i * p_sat(theta_i)
    return theta_z_psat(pi / phi_si_max), theta_z_psat(pi)


# --------------------------------------------------------------------------------------------------
@dataclass
class WynikPsi:
    grupy: tuple[str, str]
    L2D: float
    sum_Ul_e: float
    sum_Ul_i: float
    elementy: list = field(default_factory=list)    # [nazwa, U, l_e, l_i, U·l_e, U·l_i]

    @property
    def psi_e(self) -> float:
        return self.L2D - self.sum_Ul_e

    @property
    def psi_i(self) -> float:
        return self.L2D - self.sum_Ul_i


@dataclass
class WynikWezla:
    wezel: Wezel
    siatki: list                  # [(opis, n, Φ)]
    zmiana: float                 # względna zmiana Φ przy ostatnim podwojeniu
    zbieznosc_ok: bool
    bilans: float
    L: dict                       # {(a, b): L_ab}
    psi: list                     # [WynikPsi]
    theta: dict                   # temperatury grup
    f: dict                       # wyniki f_Rsi
    roz_psi: Rozwiazanie
    roz_f: Rozwiazanie
    wykresy: dict = field(default_factory=dict)
    fRsi_min: float = 0.72
    fRsi_min_zrodlo: str = ""

    @property
    def psi_glowne(self) -> WynikPsi | None:
        for p in self.psi:
            if set(p.grupy) == {"i", "e"}:
                return p
        return self.psi[0] if self.psi else None

    @property
    def fRsi_ok(self) -> bool:
        return self.f["f_Rsi"] >= self.fRsi_min - 1e-9


# --------------------------------------------------------------------------------------------------
def _rozwiaz_zbieznie(wezel: Wezel, siatka: Siatka | None = None, tryb: str = "psi", h_min=None, h_max=None,
                      max_podwojen: int = 2):
    s = siatka or siatka_dla_wezla(wezel, h_min=h_min, h_max=h_max)
    m = ModelMOS(wezel, s, tryb)
    r = m.rozwiaz()
    hist = [(s.opis(), s.n, r.Phi_calk())]
    zmiana = float("nan")
    for _ in range(max_podwojen):
        s2 = s.podwojona()
        if s2.n > MAX_KOMOREK:
            break
        m2 = ModelMOS(wezel, s2, tryb)
        r2 = m2.rozwiaz()
        hist.append((s2.opis(), s2.n, r2.Phi_calk()))
        zmiana = abs(hist[-1][2] - hist[-2][2]) / abs(hist[-1][2])
        s, m, r = s2, m2, r2
        if zmiana < KRYT_ZBIEZNOSCI:
            break
    return s, m, r, hist, zmiana


def macierz_L(model: ModelMOS) -> dict[tuple[str, str], float]:
    """Współczynniki sprzężenia L_ab [W/(m·K)] (ISO 10211 — superpozycja: θ_a = 1, pozostałe 0)."""
    grupy = model.wezel.grupy()
    jedn = model.rozwiaz_jednostkowe(grupy)
    L = {}
    for a in grupy:
        Pa = jedn[a].Phi_grup()
        for b in grupy:
            if b != a:
                L[(a, b)] = -Pa.get(b, 0.0)
    # symetryzacja (różnice na poziomie błędu maszynowego)
    for (a, b) in list(L):
        if (b, a) in L:
            v = 0.5 * (L[(a, b)] + L[(b, a)])
            L[(a, b)] = L[(b, a)] = v
    return L


def L2D_prosty(wezel: Wezel) -> float:
    """L_2D węzła o dwóch grupach (i, e) — np. podmodel okna bez ściany."""
    s, m, r, hist, zm = _rozwiaz_zbieznie(wezel)
    th = wezel.theta_grup()
    a, b = wezel.grupy()[:2]
    return abs(r.Phi_grup()[a]) / abs(th[a] - th[b])


def oblicz_wezel(wezel: Wezel, h_min: float | None = None, h_max: float | None = None,
                 katalog_wykresow: str | Path | None = None, fRsi_min: float | None = None) -> WynikWezla:
    s, m, r, hist, zmiana = _rozwiaz_zbieznie(wezel, h_min=h_min, h_max=h_max)
    L = macierz_L(m)
    th = wezel.theta_grup()
    # ψ dla par grup, między którymi są elementy flankujące
    pary: list[tuple[str, str]] = []
    for el in wezel.flankujace:
        p = tuple(el.grupy)
        if p not in pary and p[::-1] not in pary:
            pary.append(p)
    if not pary and len(th) == 2:
        pary.append(tuple(wezel.grupy()))
    psi = []
    for (a, b) in pary:
        Lab = L.get((a, b), 0.0)
        se = si = 0.0
        els = []
        for el in wezel.flankujace:
            if set(el.grupy) != {a, b}:
                continue
            if el.wezel_ref is not None:
                Lr = L2D_prosty(el.wezel_ref)
                se += Lr
                si += Lr
                els.append([el.nazwa, "L_2D = " + f_(Lr, 4), "—", "—", Lr, Lr])
            else:
                U = el.U_obl()
                se += U * el.l_e
                si += U * el.l_i
                els.append([el.nazwa, U, el.l_e, el.l_i, U * el.l_e, U * el.l_i])
        psi.append(WynikPsi((a, b), Lab, se, si, els))
    # f_Rsi
    mf = ModelMOS(wezel, s, "fRsi")
    rf = mf.rozwiaz()
    tmin, xm, ym, k = rf.theta_si_min("wewn", bez_okien=True)
    ti = th.get("i", max(th.values()))
    te = th.get("e", min(th.values()))
    fR = (tmin - te) / (ti - te)
    f = {"theta_si_min": tmin, "x": xm, "y": ym, "f_Rsi": fR, "theta_i": ti, "theta_e": te}
    okn = rf.powierzchnie("wewn") & np.isin(mf.b.rodzaj_mat, ["rama", "szyba"])
    if okn.any():
        tp = np.where(okn, rf.theta_pow, np.inf)
        ko = int(np.argmin(tp))
        f["theta_si_min_okno"] = float(tp[ko])
        f["f_Rsi_okno"] = (float(tp[ko]) - te) / (ti - te)
    if len(th) > 2:
        jedn = mf.rozwiaz_jednostkowe(wezel.grupy())
        f["g"] = {g: jedn[g].theta_powierzchni(xm, ym, k) for g in wezel.grupy()}
    tk, tdp = theta_krytyczne(ti)
    f["theta_krytyczna_80"] = tk
    f["theta_rosy"] = tdp
    f["f_krytyczne_obl"] = (tk - te) / (ti - te)
    fmin, zr = (fRsi_min, "zadane") if fRsi_min is not None else _wym("fRsi_min", "energia", 0.72)
    w = WynikWezla(wezel, hist, zmiana, bool(zmiana < KRYT_ZBIEZNOSCI) if math.isfinite(zmiana) else False,
                   r.bilans(), L, psi, th, f, r, rf, fRsi_min=fmin, fRsi_min_zrodlo=zr)
    if katalog_wykresow:
        w.wykresy = rysuj_wszystko(w, katalog_wykresow)
    return w


# --------------------------------------------------------------------------------------------------
# Wykresy
# --------------------------------------------------------------------------------------------------
def _widok(w: Wezel):
    if w.widok:
        return w.widok
    from shapely.ops import unary_union
    return unary_union([o.wielobok for o in w.obszary]).bounds


def _kontury(ax, wezel: Wezel, widok):
    from shapely.geometry import box as _box
    vb = _box(*widok).buffer(0.05)
    for o in wezel.obszary:
        g = o.wielobok.intersection(vb)
        for part in getattr(g, "geoms", [g]):
            if part.is_empty or not hasattr(part, "exterior"):
                continue
            for rg in [part.exterior] + list(part.interiors):
                xy = np.asarray(rg.coords)
                ax.plot(xy[:, 0], xy[:, 1], color="#222222", lw=0.45, zorder=3)


def _ax_setup(ax, widok, tytul):
    ax.set_xlim(widok[0], widok[2])
    ax.set_ylim(widok[1], widok[3])
    ax.set_aspect("equal")
    ax.set_title(tytul, fontsize=9)
    ax.set_xlabel("x [m]", fontsize=8)
    ax.set_ylabel("y [m]", fontsize=8)
    ax.tick_params(labelsize=7)


def rysuj_mape(w: WynikWezla, plik: str | Path, roz: Rozwiazanie | None = None, tytul: str | None = None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    roz = roz or w.roz_psi
    s = roz.model.s
    T = np.ma.masked_invalid(roz.T)
    widok = _widok(w.wezel)
    th = list(w.theta.values())
    lo, hi = min(th), max(th)
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=150)
    pc = ax.pcolormesh(s.x, s.y, T, cmap="RdYlBu_r", vmin=lo, vmax=hi, shading="flat", zorder=1)
    krok = 2.0 if hi - lo > 20 else 1.0
    lev = np.arange(math.ceil(lo / krok) * krok, hi + 1e-9, krok)
    cs = ax.contour(s.xc, s.yc, T, levels=lev, colors="k", linewidths=0.35, zorder=2)
    ax.clabel(cs, lev[::2], fontsize=5, fmt="%.0f")
    lim = w.f["theta_e"] + w.fRsi_min * (w.f["theta_i"] - w.f["theta_e"])
    Tf = np.ma.masked_invalid(w.roz_f.T) if w.roz_f.model.s is s else T
    ax.contour(s.xc, s.yc, Tf, levels=[lim], colors="#c0007a", linewidths=1.0, linestyles="--", zorder=4)
    _kontury(ax, w.wezel, widok)
    ax.plot([w.f["x"]], [w.f["y"]], marker="o", mfc="none", mec="#c0007a", ms=7, zorder=5)
    cb = fig.colorbar(pc, ax=ax, shrink=0.8)
    cb.set_label("θ [°C]", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    _ax_setup(ax, widok, tytul or f"{w.wezel.id} — rozkład temperatury (R_s wg ISO 6946), izotermy co {krok:g} K;\n"
                                     f"przerywana: izoterma θ = {lim:.1f} °C (f = {w.fRsi_min}) przy R_si = 0,25; ○ θ_si,min")
    fig.tight_layout()
    fig.savefig(plik)
    plt.close(fig)


def rysuj_strumien(w: WynikWezla, plik: str | Path, n_strzalek: int = 28):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    roz = w.roz_psi
    s = roz.model.s
    qx, qy = roz.strumien_komorek()
    q = np.hypot(qx, qy)
    widok = _widok(w.wezel)
    fig, ax = plt.subplots(figsize=(7.2, 6.0), dpi=150)
    qm = np.ma.masked_invalid(np.where(q > 0, q, np.nan))
    vmin = max(float(np.nanpercentile(q, 2)), 1e-3) if np.isfinite(q).any() else 1e-3
    pc = ax.pcolormesh(s.x, s.y, qm, cmap="magma_r", norm=LogNorm(vmin=vmin, vmax=float(np.nanmax(q))),
                       shading="flat", zorder=1)
    xs = np.linspace(widok[0], widok[2], n_strzalek + 2)[1:-1]
    ys = np.linspace(widok[1], widok[3], int(n_strzalek * (widok[3] - widok[1]) / (widok[2] - widok[0])) + 2)[1:-1]
    X, Y = np.meshgrid(xs, ys)
    ii = np.clip(np.searchsorted(s.x, X) - 1, 0, s.nx - 1)
    jj = np.clip(np.searchsorted(s.y, Y) - 1, 0, s.ny - 1)
    U, V = qx[jj, ii], qy[jj, ii]
    M = np.hypot(U, V)
    ok = np.isfinite(M) & (M > 0)
    ax.quiver(X[ok], Y[ok], U[ok] / M[ok], V[ok] / M[ok], color="#1f5fa8", scale=n_strzalek * 1.6, width=0.0022,
              zorder=4)
    _kontury(ax, w.wezel, widok)
    cb = fig.colorbar(pc, ax=ax, shrink=0.8)
    cb.set_label("|q| [W/m²] (skala log.)", fontsize=8)
    cb.ax.tick_params(labelsize=7)
    _ax_setup(ax, widok, f"{w.wezel.id} — gęstość i kierunek strumienia ciepła (wektory jednostkowe)")
    fig.tight_layout()
    fig.savefig(plik)
    plt.close(fig)


def lancuchy_powierzchni(roz: Rozwiazanie, maska: np.ndarray) -> list[np.ndarray]:
    """Porządkuje ściany brzegowe (maska) w łańcuchy wzdłuż powierzchni → lista tablic indeksów."""
    b = roz.model.b
    idx = np.nonzero(maska)[0]
    if len(idx) == 0:
        return []
    key = lambda x, y: (round(float(x), 9), round(float(y), 9))
    adj: dict = {}
    for k in idx:
        for p in (key(b.x0[k], b.y0[k]), key(b.x1[k], b.y1[k])):
            adj.setdefault(p, []).append(k)
    uzyte = set()
    out = []
    konce = [p for p, v in adj.items() if len(v) == 1]
    starty = konce + list(adj.keys())
    for p0 in starty:
        wolne = [k for k in adj[p0] if k not in uzyte]
        if not wolne:
            continue
        chain = []
        p = p0
        k = wolne[0]
        while k is not None:
            uzyte.add(k)
            chain.append(k)
            a, c = key(b.x0[k], b.y0[k]), key(b.x1[k], b.y1[k])
            p = c if a == p else a
            nast = [kk for kk in adj[p] if kk not in uzyte]
            k = nast[0] if nast else None
        out.append(np.array(chain))
    return out


def rysuj_powierzchnie(w: WynikWezla, plik: str | Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rf = w.roz_f
    b = rf.model.b
    tp = rf.theta_pow
    maska = rf.powierzchnie("wewn")
    lan = lancuchy_powierzchni(rf, maska)
    ti, te = w.f["theta_i"], w.f["theta_e"]
    lim = te + w.fRsi_min * (ti - te)
    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=150)
    for n, ch in enumerate(sorted(lan, key=len, reverse=True)[:4]):
        dl = b.dl[ch]
        sc = np.cumsum(dl) - dl / 2
        nazwa = w.wezel.strefy[int(b.strefa[ch[0]])].nazwa
        ax.plot(sc, tp[ch], lw=1.2, label=f"{nazwa} (łańcuch {n + 1})")
    ax.axhline(lim, color="#c0007a", ls="--", lw=1.0, label=f"θ dla f_Rsi,min = {w.fRsi_min} ({lim:.1f} °C)")
    ax.axhline(w.f["theta_krytyczna_80"], color="#e08a00", ls=":", lw=1.0,
               label=f"θ_si,kryt (φ_si = 80 %, φ_i = 50 %) = {w.f['theta_krytyczna_80']:.1f} °C")
    ax.set_xlabel("współrzędna wzdłuż powierzchni wewnętrznej s [m]", fontsize=8)
    ax.set_ylabel("θ_si [°C]", fontsize=8)
    ax.set_title(f"{w.wezel.id} — temperatura powierzchni wewnętrznej (R_si = 0,25; θ_i = {ti:g}, θ_e = {te:g} °C); "
                 f"min {w.f['theta_si_min']:.2f} °C, f_Rsi = {w.f['f_Rsi']:.3f}", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=6, loc="lower right")
    fig.tight_layout()
    fig.savefig(plik)
    plt.close(fig)


def rysuj_wszystko(w: WynikWezla, katalog: str | Path) -> dict[str, str]:
    k = Path(katalog)
    k.mkdir(parents=True, exist_ok=True)
    out = {"temperatura": k / f"{w.wezel.id}_temperatura.png", "strumien": k / f"{w.wezel.id}_strumien.png",
           "powierzchnia": k / f"{w.wezel.id}_theta_si.png"}
    rysuj_mape(w, out["temperatura"])
    rysuj_strumien(w, out["strumien"])
    rysuj_powierzchnie(w, out["powierzchnia"])
    return {a: str(p) for a, p in out.items()}


# --------------------------------------------------------------------------------------------------
# Raport
# --------------------------------------------------------------------------------------------------
def _Rs_opis(st) -> str:
    if isinstance(st.Rs, dict):
        return "wg ISO 6946: 0,13 poziomo / 0,10 w górę / 0,17 w dół"
    return f_(st.Rs, 2)


def _tab(nagl, wiersze) -> str:
    out = ["| " + " | ".join(nagl) + " |", "|" + "|".join("---" for _ in nagl) + "|"]
    for w in wiersze:
        out.append("| " + " | ".join(f_(v, 4) if isinstance(v, float) else ("—" if v is None else str(v))
                                     for v in w) + " |")
    return "\n".join(out)


def raport_wezla(w: WynikWezla, katalog_raportu: str | Path | None = None) -> str:
    wz = w.wezel
    rel = (lambda p: str(Path(p).relative_to(Path(katalog_raportu)))) if katalog_raportu else (lambda p: str(p))
    L = [f"## {wz.id} — {wz.nazwa}", ""]
    if wz.opis:
        L += [wz.opis, ""]
    L += ["**Dane wejściowe**", ""]
    for k, v in wz.dane.items():
        if isinstance(v, list) and v and isinstance(v[0], list):
            L += ["", f"*{k}:*", "", _tab(["kod", "materiał", "d [m]", "λ [W/(m·K)]", "R [m²K/W]"], v), ""]
        elif isinstance(v, list):
            continue
        else:
            L.append(f"* {k}: {v if not isinstance(v, float) else f_(v, 3)}")
    L += ["", "**Warunki brzegowe** (przekrój " + wz.przekroj + "; płaszczyzny odcięcia i osie symetrii adiabatyczne)", "",
          _tab(["strefa", "rodzaj", "grupa", "θ [°C]", "R_s — przebieg ψ [m²K/W]", "R_s — przebieg f_Rsi"],
               [[st.nazwa, st.rodzaj, st.grupa, f_(st.theta, 1), _Rs_opis(st),
                 "0,25 (ramy/szyby 0,13)" if st.rodzaj == "wewn" else _Rs_opis(st)] for st in wz.strefy]), ""]
    L += ["**Siatka i dokładność** (MOS, siatka prostokątna zagęszczana przy granicach materiałów)", "",
          _tab(["siatka", "komórek", "Φ_całk [W/m]"], [[o, str(n), phi] for o, n, phi in w.siatki]), "",
          f"Zmiana strumienia przy podwojeniu liczby podziałów: **{f_(100 * w.zmiana, 3)} %** "
          f"(kryterium ISO 10211 < 1 %: {'spełnione' if w.zbieznosc_ok else 'NIESPEŁNIONE'}); "
          f"bilans energii Σ Φ / (½ Σ|Φ|) = {w.bilans:.1e} (kryterium < 10⁻⁴: "
          f"{'spełnione' if w.bilans < KRYT_BILANSU else 'NIESPEŁNIONE'}).", ""]
    L += ["**Współczynniki sprzężenia i ψ**", ""]
    if len(w.theta) > 2:
        L += [_tab(["para grup", "L_2D [W/(m·K)]"], [[f"{a}–{b}", v] for (a, b), v in w.L.items() if a < b]), ""]
    for p in w.psi:
        L += [f"*Para {p.grupy[0]}–{p.grupy[1]}:* L_2D = **{f_(p.L2D, 4)} W/(m·K)**", "",
              _tab(["element flankujący", "U [W/(m²K)]", "l_e [m]", "l_i [m]", "U·l_e", "U·l_i"], p.elementy), "",
              f"ψ_e (wymiary zewnętrzne) = {f_(p.L2D, 4)} − {f_(p.sum_Ul_e, 4)} = **{f_(p.psi_e, 3)} W/(m·K)**; "
              f"ψ_i (wymiary wewnętrzne) = {f_(p.L2D, 4)} − {f_(p.sum_Ul_i, 4)} = **{f_(p.psi_i, 3)} W/(m·K)**", ""]
    fr = w.f
    L += ["**Temperatura powierzchni wewnętrznej i ryzyko pleśni** (R_si = 0,25 — PN-EN ISO 13788)", "",
          f"* θ_si,min = **{f_(fr['theta_si_min'], 2)} °C** w punkcie ({f_(fr['x'], 3)}; {f_(fr['y'], 3)}) m "
          f"przy θ_i = {f_(fr['theta_i'], 1)} °C, θ_e = {f_(fr['theta_e'], 1)} °C",
          f"* f_Rsi = (θ_si,min − θ_e)/(θ_i − θ_e) = **{f_(fr['f_Rsi'], 3)}**; wymaganie f_Rsi ≥ {f_(w.fRsi_min, 2)} "
          f"({w.fRsi_min_zrodlo}) → **{'SPEŁNIA' if w.fRsi_ok else 'NIE SPEŁNIA'}**"]
    if "f_Rsi_okno" in fr:
        L.append(f"* rama/szyba (R_si = 0,13): θ_si,min = {f_(fr['theta_si_min_okno'], 2)} °C, "
                 f"f_Rsi = {f_(fr['f_Rsi_okno'], 3)} (informacyjnie — ocena okna wg PN-EN ISO 10077-2/13788)")
    if "g" in fr:
        L.append("* współczynniki wagowe θ_si = Σ g·θ: " + ", ".join(f"g_{k} = {f_(v, 3)}" for k, v in fr["g"].items()))
    L.append(f"* informacyjnie przy θ_e obliczeniowej i φ_i = 50 %: θ_si,kryt (φ_si = 80 %) = "
             f"{f_(fr['theta_krytyczna_80'], 1)} °C (f = {f_(fr['f_krytyczne_obl'], 3)}), punkt rosy "
             f"{f_(fr['theta_rosy'], 1)} °C → θ_si,min {'≥' if fr['theta_si_min'] >= fr['theta_krytyczna_80'] else '<'}"
             f" θ_si,kryt (ocena miesięczna wg ISO 13788 — łagodniejsza; kryterium formalne: f_Rsi ≥ {f_(w.fRsi_min, 2)})")
    L.append("")
    pg = w.psi_glowne
    if pg and (wz.psi_domyslne or wz.psi_deklarowane):
        L += ["**Porównanie**", ""]
        if wz.psi_domyslne and wz.psi_domyslne in PSI_DOMYSLNE_14683:
            d = PSI_DOMYSLNE_14683[wz.psi_domyslne]
            L.append(f"* PN-EN ISO 14683 — wartość domyślna ({d['opis']}): ψ_e = {f_(d['psi_e'], 2)}, "
                     f"ψ_i = {f_(d['psi_i'], 2)} W/(m·K) {d['status']} — obliczone ψ_e = {f_(pg.psi_e, 3)}, "
                     f"ψ_i = {f_(pg.psi_i, 3)} ({'poniżej' if pg.psi_e <= d['psi_e'] else 'POWYŻEJ'} wartości domyślnej)")
        if wz.psi_deklarowane:
            d = wz.psi_deklarowane
            L.append(f"* deklaracja wyrobu: ψ = {f_(d.get('psi'), 3)} W/(m·K)"
                     + (f", f_Rsi = {f_(d.get('f_Rsi'), 2)}" if d.get("f_Rsi") is not None else "")
                     + f" — {d.get('zrodlo', '')}; obliczone ψ_e = {f_(pg.psi_e, 3)}, f_Rsi = {f_(fr['f_Rsi'], 3)}")
        L.append("")
    for u in wz.uwagi:
        L.append(f"*Uwaga:* {u}")
    if wz.uwagi:
        L.append("")
    if w.wykresy:
        L += [f"![{wz.id} — temperatura]({rel(w.wykresy['temperatura'])})", "",
              f"![{wz.id} — strumień]({rel(w.wykresy['strumien'])})", "",
              f"![{wz.id} — θ_si]({rel(w.wykresy['powierzchnia'])})", ""]
    return "\n".join(L)


def tabela_zbiorcza(wyniki: Sequence[WynikWezla]) -> str:
    wiersze = []
    for w in wyniki:
        p = w.psi_glowne
        wiersze.append([w.wezel.id, w.wezel.nazwa, f_(p.L2D, 4) if p else "—", f_(p.psi_e, 3) if p else "—",
                        f_(p.psi_i, 3) if p else "—", f_(w.f["theta_si_min"], 2), f_(w.f["f_Rsi"], 3),
                        "tak" if w.fRsi_ok else "**NIE**", f_(100 * w.zmiana, 2) + " %"])
    return _tab(["węzeł", "nazwa", "L_2D (i–e)", "ψ_e", "ψ_i", "θ_si,min [°C]", "f_Rsi", "f_Rsi ≥ min", "Δ siatki"],
                wiersze)


def zestawienie_HTB(wyniki: Sequence[WynikWezla], dlugosci: dict[str, float], system: str = "e") -> tuple[float, list]:
    """H_TB = Σ ψ_k·l_k [W/K] z wartości symulowanych (system wymiarów 'e' lub 'i' — zgodny z pomiarem pól U·A)."""
    tot = 0.0
    wiersze = []
    for w in wyniki:
        l = dlugosci.get(w.wezel.id)
        p = w.psi_glowne
        if l is None or p is None:
            continue
        psi = p.psi_e if system == "e" else p.psi_i
        tot += psi * l
        wiersze.append([w.wezel.id, w.wezel.nazwa, psi, l, psi * l])
    return tot, wiersze


def raport_katalogu(wyniki: Sequence[WynikWezla], plik: str | Path, tytul: str, wstep: str = "",
                    dlugosci: dict[str, float] | None = None, walidacja_md: str | None = None) -> str:
    plik = Path(plik)
    L = [f"# {tytul}", "", wstep, "",
         "Podstawy: PN-EN ISO 10211:2017-09 (metoda numeryczna 2D, warunki brzegowe, płaszczyzny odcięcia, kryteria "
         "dokładności), PN-EN ISO 14683:2017-09 (ψ w wymiarach zewnętrznych i wewnętrznych), PN-EN ISO 13788:2013-05 "
         "(f_Rsi, R_si = 0,25), PN-EN ISO 6946:2017-10 (R_si/R_se, pustki powietrzne), PN-EN ISO 13370:2017-09 "
         "(grunt), WT zał. 2 pkt 2.2 (f_Rsi ≥ 0,72 — W-248). Solver: `lamela.obliczenia.mostki2d` (walidacja "
         "wg zał. C ISO 10211 — " + (walidacja_md or "patrz raport walidacji") + ").", "",
         "## Zestawienie", "", tabela_zbiorcza(wyniki), ""]
    if dlugosci:
        H, wiersze = zestawienie_HTB(wyniki, dlugosci)
        L += ["## H_TB (wymiary zewnętrzne)", "",
              _tab(["węzeł", "nazwa", "ψ_e [W/(m·K)]", "l [m]", "ψ·l [W/K]"], wiersze), "",
              f"**H_TB = Σ ψ_e·l = {f_(H, 2)} W/K**", ""]
    for w in wyniki:
        L += [raport_wezla(w, plik.parent), ""]
    txt = "\n".join(L)
    plik.parent.mkdir(parents=True, exist_ok=True)
    plik.write_text(txt, encoding="utf-8")
    return txt
