"""Dodatkowe węzły 2D (PN-EN ISO 10211) — geometrie spotykane w modelu „Dom LAMELA”, nieobjęte budowniczymi
`geometria.py`:

* `wezel_wspornik_ogolny` — płyta stropu z płytą wspornikową (inna grubość / rzędna wierzchu niż strop, łącznik
  termoizolacyjny), ściana dolna i górna o różnych warstwach, pod stropem pomieszczenie ogrzewane ALBO powietrze
  zewnętrzne z ociepleniem spodu (strop nad powietrzem — wspornik bryły), belka odwrócona w linii ściany górnej;
* `wezel_attyka_wspornik` — attyka stropodachu w licu ściany + płyta wspornikowa (okap) stropodachu przez łącznik;
* `wezel_przegroda_w_linii` — płyta ciągła nad przegrodą pionową (ściana dom–garaż, ściana wewnętrzna pod ścianą
  zewnętrzną wyższej kondygnacji, ściana zewnętrzna pod stropem nad powietrzem): po każdej stronie nad płytą
  pomieszczenie (podłoga) albo zewnętrze (dach), pod płytą pomieszczenie ogrzewane / nieogrzewane / zewnętrze
  (sufit, pas docieplenia), opcjonalnie ściana na płycie w tej samej linii — 2 lub 3 temperatury;
* `wezel_garaz_plyta` — ściana dom–garaż na ciągłej płycie fundamentowej (XPS pod całą płytą).

Konwencje jak w `geometria.py`: wnętrze / strona „lewa” x < 0, lico lewe ściany x = 0, spód płyty y = 0,
płaszczyzny odcięcia max(1 m; 3·d) adiabatyczne. Warstwy przegród z modelu (ściany od wnętrza = od strony lewej,
poziome od góry). Warstwy powietrza dobrze wentylowane (np. pustka pod podsufitką) i warstwy za nimi pominięte
(PN-EN ISO 6946). Założenia oznaczone [ZAŁ] opisane w `Wezel.dane` / `Wezel.uwagi`.
"""
from __future__ import annotations

from typing import Sequence

from shapely.geometry import box

from .geometria import (LACZNIK_PRZYKLAD, MATERIALY_DOMYSLNE, RSI_DOL, RSI_GORA, RSI_POZIOMO, S_STREFY,
                        ElementFlankujacy, Material, Warstwa, Wezel, _izolacja_najlepsza, _ln, _nas, _obsz, _stos,
                        _temperatury, dane_warstw, grubosc, indeks_konstrukcyjnej, odl_ciecia,
                        pomin_pustki_wentylowane, strefy_z_dopelnienia)

GRUPY = {"wewn": "i", "zewn": "e", "nieogrz": "u"}


def _bez_went_sufit(warstwy: Sequence[Warstwa]) -> list[Warstwa]:
    """Warstwy sufitu (od płyty w dół = od strony ciepłej): pomija pustkę wentylowaną i warstwy pod nią."""
    return pomin_pustki_wentylowane(list(warstwy), zewn_na_poczatku=False)


def _bez_went_dach(warstwy: Sequence[Warstwa]) -> list[Warstwa]:
    return pomin_pustki_wentylowane(list(warstwy), zewn_na_poczatku=True)


def _theta_u(ti: float, te: float, theta_u: float | None, b_u: float) -> float:
    return theta_u if theta_u is not None else te + (1 - b_u) * (ti - te)


# ==================================================================================================
# A. Płyta wspornikowa — wariant ogólny
# ==================================================================================================
def wezel_wspornik_ogolny(sciana_gora: Sequence[Warstwa], sciana_dol: Sequence[Warstwa] | None,
                          t_plyty: float, mat_plyty: Material, podloga: Sequence[Warstwa] = (),
                          sufit: Sequence[Warstwa] = (), pod: str = "wewn",
                          t_wsp: float | None = None, dy_wsp: float = 0.0, mat_wsp: Material | None = None,
                          wysieg: float = 1.0, lacznik: Material | None = LACZNIK_PRZYKLAD, d_lacznika: float = 0.08,
                          belka: tuple[float, float] | None = None, mat_belki: Material | None = None,
                          H: float | None = None, L_in: float | None = None, theta_i: float | None = None,
                          theta_e: float | None = None, id: str = "WZ-B", nazwa: str | None = None) -> Wezel:
    """Strop + płyta wspornikowa (przekrój pionowy). Wnętrze x < 0, lico wewn. ścian x = 0, płyta stropu
    y ∈ [0, t_plyty]; wspornik: grubość t_wsp, wierzch na rzędnej t_plyty + dy_wsp, od lica zewn. konstrukcji ściany
    (łącznik d_lacznika w warstwie ocieplenia) do lica zewn. + wysieg (wysieg = 0 — bez wspornika).
    pod = 'wewn' — pod stropem pomieszczenie ogrzewane ze ścianą `sciana_dol`; 'zewn' — strop nad powietrzem
    zewnętrznym: pod płytą ocieplenie `sufit` (do lica zewn. ściany górnej), bez ściany dolnej.
    belka = (b, h_nad_plyta) — belka odwrócona (np. wspornikowa / krawędziowa) w miejscu warstwy konstrukcyjnej
    ściany górnej od wierzchu płyty na wysokość h_nad_plyta (mat_belki)."""
    ti, te = _temperatury(theta_i, theta_e)
    t = t_plyty
    t_w = t_wsp or t
    y_w1 = t + dy_wsp
    y_w0 = y_w1 - t_w
    mat_wsp = mat_wsp or mat_plyty
    st_g = _stos(sciana_gora, 0.0)
    kg = indeks_konstrukcyjnej(sciana_gora)
    x_s1 = st_g[kg][1]
    x_out = st_g[-1][1]
    sufit = _bez_went_sufit(sufit) if pod == "zewn" else list(sufit)
    t_pod, t_suf = grubosc(podloga), grubosc(sufit)
    H = H or odl_ciecia(x_out)
    L_in = L_in or odl_ciecia(t + t_pod + t_suf)
    x_end = x_out + wysieg if wysieg > 0 else x_s1
    ob = []
    # ściana górna (od wierzchu płyty; warstwy zewnętrzne także przy płycie — nadpisuje je płyta / łącznik)
    y_dol_zewn = (-t_suf if pod == "zewn" else -H)
    for k, (a, b, w) in enumerate(st_g):
        if k <= kg:
            ob.append(_obsz(box(a, t, b, t + H), w))
        else:
            ob.append(_obsz(box(a, y_dol_zewn, b, t + H), w))
    if belka:
        b_b, h_b = belka
        ob.append(_obsz(box(x_s1 - b_b, t, x_s1, t + h_b), mat_belki or mat_wsp, "belka odwrócona"))
    # ściana dolna
    if pod == "wewn" and sciana_dol:
        st_d = _stos(sciana_dol, 0.0)
        kd = indeks_konstrukcyjnej(sciana_dol)
        for k, (a, b, w) in enumerate(st_d):
            ob.append(_obsz(box(a, -H, b, 0.0 if k <= kd else y_w0 if wysieg > 0 else t), w))
    for y0, y1, w in _stos(podloga, t + t_pod, -1):
        ob.append(_obsz(box(-L_in, y0, 0.0, y1), w))
    x_suf1 = 0.0 if pod == "wewn" else x_out
    for y0, y1, w in _stos(sufit, 0.0, -1):
        ob.append(_obsz(box(-L_in, y0, x_suf1, y1), w))
    ob.append(_obsz(box(-L_in, 0.0, x_s1, t), mat_plyty, "płyta stropu"))
    if wysieg > 0:
        ob.append(_obsz(box(x_s1, y_w0, x_end, y_w1), mat_wsp, "płyta wspornikowa"))
        if lacznik is not None:
            ob.append(_obsz(box(x_s1, y_w0, x_s1 + d_lacznika, y_w1), lacznik))
    S = S_STREFY
    y_min = -H if pod == "wewn" else -t_suf - H
    ramka = box(-L_in, y_min, max(x_end, x_out) + S, t + H)
    nas = [((-L_in / 2, t + t_pod + (H - t_pod) / 2), _nas("pomieszczenie górne", ti, "wewn")),
           ((x_out + S / 2, t + H - 0.02), _nas("zewnętrze", te, "zewn"))]
    if pod == "wewn":
        nas.append(((-L_in / 2, -H / 2), _nas("pomieszczenie dolne", ti, "wewn")))
    fl = [ElementFlankujacy("ściana górna", ("i", "e"), H + t / 2 if pod == "wewn" else H + t + t_suf,
                            H - t_pod, warstwy=list(sciana_gora), l_oi=H - t_pod)]
    if pod == "wewn":
        fl.append(ElementFlankujacy("ściana dolna", ("i", "e"), H + t / 2, H - t_suf,
                                    warstwy=list(sciana_dol or sciana_gora), l_oi=H + t + t_pod))
    else:
        warstwy_st = list(podloga) + [Warstwa(mat_plyty, t, True)] + list(sufit)
        fl.append(ElementFlankujacy("strop nad powietrzem zewn.", ("i", "e"), L_in + x_out, L_in,
                                    warstwy=warstwy_st, Rsi=RSI_DOL, l_oi=L_in))
    strefy = strefy_z_dopelnienia(ob, ramka, nas)
    return _wynik_wspornika(id, nazwa, ob, strefy, fl, dict(
        t=t, t_w=t_w, y_w0=y_w0, y_w1=y_w1, x_s1=x_s1, x_out=x_out, x_end=x_end, t_pod=t_pod, t_suf=t_suf,
        L_in=L_in, H=H, pod=pod, wysieg=wysieg, lacznik=lacznik, d_l=d_lacznika, belka=belka,
        sciana_gora=sciana_gora, sciana_dol=sciana_dol, podloga=podloga, sufit=sufit, mat_plyty=mat_plyty,
        mat_wsp=mat_wsp))


def _wynik_wspornika(id, nazwa, ob, strefy, fl, g: dict) -> Wezel:
    t, x_out, x_end, x_s1 = g["t"], g["x_out"], g["x_end"], g["x_s1"]
    wys = g["wysieg"]
    lac = g["lacznik"]
    linie = []
    if wys > 0:
        h_w = 0.15 + 0.03       # wywinięcie hydroizolacji ≥ 15 cm ponad powierzchnię płyty (+ obróbka) [ZAŁ]
        yw = g["y_w1"]
        linie = [_ln("hydro", [(x_end, yw + 0.004), (x_out + 0.004, yw + 0.004), (x_out + 0.004, yw + h_w)],
                     "membrana płyty wspornikowej wywinięta na ścianę ≥ 15 cm ponad powierzchnię płyty"),
                 _ln("obrobka", [(x_end - 0.10, yw + 0.006), (x_end + 0.03, yw + 0.006), (x_end + 0.03, yw - 0.05),
                                 (x_end + 0.045, yw - 0.065)], "obróbka czoła płyty z okapnikiem ≥ 3 cm"),
                 _ln("woda", [(x_out + 0.12, yw + 0.05), (x_out + max(0.25, min(0.9, wys - 0.1)), yw + 0.05)],
                     "spadek płyty ≥ 2 % od budynku")]
    if g["pod"] == "zewn":
        linie.append(_ln("paro", [(-g["L_in"], t + g["t_pod"] + 0.002), (0.0, t + g["t_pod"] + 0.002)],
                         "szczelność powietrzna: płyta ŻB + tynk ściany górnej doprowadzony do płyty"))
    typ = "strop_zewn_krawedz" if g["pod"] == "zewn" else ("wspornik" if wys > 0 else "strop_posredni")
    nm = nazwa or {"strop_zewn_krawedz": "Strop nad powietrzem zewnętrznym — krawędź ze ścianą",
                   "wspornik": "Płyta wspornikowa z łącznikiem termoizolacyjnym",
                   "strop_posredni": "Strop pośredni"}[typ]
    dane = {"warstwy ściany górnej": dane_warstw(g["sciana_gora"]),
            "warstwy ściany dolnej": dane_warstw(g["sciana_dol"] or []) if g["pod"] == "wewn" else "— (pod stropem "
                                                                                                   "powietrze zewn.)",
            "płyta": f"{g['mat_plyty'].kod}, t = {t} m",
            "warstwy podłogi": dane_warstw(g["podloga"]), "warstwy sufitu (bez pustki wentylowanej)": dane_warstw(g["sufit"])}
    if wys > 0:
        dane["płyta wspornikowa"] = (f"{g['mat_wsp'].kod}, t = {g['t_w']} m, wierzch {g['y_w1'] - t:+.2f} m wzgl. "
                                     f"wierzchu stropu, wysięg {wys} m od lica ocieplenia")
        dane["łącznik"] = (f"{lac.nazwa}: λ_eq = {lac.lam} W/(m·K), d = {g['d_l']} m — {lac.zrodlo}" if lac
                           else "brak (płyta ciągła przez izolację)")
    if g["belka"]:
        dane["belka odwrócona"] = f"b = {g['belka'][0]} m, h nad płytą = {g['belka'][1]:.2f} m (w linii ściany górnej)"
    uw = []
    if g["pod"] == "zewn":
        uw.append("Pustka wentylowana pod ociepleniem spodu stropu i podsufitka pominięte (PN-EN ISO 6946 — warstwy "
                  "za pustką dobrze wentylowaną); R_se = 0,04 na spodzie ocieplenia (wariant ostrożny) [ZAŁ].")
    return Wezel(id, nm, typ, ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"naroże podłoga–ściana": (0.0, t + g["t_pod"])},
                 widok=(-min(g["L_in"], 1.0), -min(g["H"], 1.0) - (g["t_suf"] if g["pod"] == "zewn" else 0.0),
                        max(x_end, x_out) + 0.1, t + min(g["H"], 1.0)),
                 psi_domyslne=None, dane=dane, uwagi=uw,
                 opis="Przekrój pionowy; " + ("pod stropem powietrze zewnętrzne (ocieplenie spodu)." if g["pod"] == "zewn"
                                             else "pomieszczenia nad i pod stropem ogrzewane (grupa „i”)."))


# ==================================================================================================
# B. Attyka w licu ściany + płyta wspornikowa stropodachu (okap) przez łącznik
# ==================================================================================================
def wezel_attyka_wspornik(sciana: Sequence[Warstwa], dach: Sequence[Warstwa], attyka: Sequence[Warstwa],
                          h_nad_pokryciem: float = 0.30, d_izol_gora: float = 0.05,
                          t_wsp: float | None = None, dy_wsp: float = 0.0, mat_wsp: Material | None = None,
                          wysieg: float = 1.0, lacznik: Material | None = LACZNIK_PRZYKLAD, d_lacznika: float = 0.08,
                          blok_attyki: tuple[Material, float] | None = None,
                          H: float | None = None, L: float | None = None, theta_i: float | None = None,
                          theta_e: float | None = None, id: str = "WZ-RW", nazwa: str | None = None) -> Wezel:
    """Stropodach z attyką w licu ściany i okapem (płyta wspornikowa) przez łącznik termoizolacyjny.
    `attyka` — warstwy przegrody attyki od strony dachu: [izolacja wewn., konstrukcja, izolacja zewn., wyprawa]
    (konstrukcja attyki w linii konstrukcji ściany). Wspornik: grubość t_wsp, wierzch t_plyty + dy_wsp, od lica
    konstrukcji do lica ocieplenia + wysieg; izolacja zewnętrzna attyki opiera się na wsporniku."""
    ti, te = _temperatury(theta_i, theta_e)
    st = _stos(sciana, 0.0)
    ks = indeks_konstrukcyjnej(sciana)
    x_s0, x_s1 = st[ks][0], st[ks][1]
    x_out = st[-1][1]
    dach = _bez_went_dach(dach)
    kd = indeks_konstrukcyjnej(dach)
    nad, plyta, pod = list(dach[:kd]), dach[kd], list(dach[kd + 1:])
    t = plyta.d
    t_suf = grubosc(pod)
    y_top = t + grubosc(nad)
    y_cap = y_top + h_nad_pokryciem
    y_p = y_cap - d_izol_gora
    ka = indeks_konstrukcyjnej(attyka)
    iz_w = attyka[ka - 1] if ka > 0 else Warstwa(_izolacja_najlepsza(nad), 0.10)
    iz_z = attyka[ka + 1] if ka + 1 < len(attyka) else None
    mat_att = attyka[ka].mat
    t_w = t_wsp or t
    y_w1 = t + dy_wsp
    y_w0 = y_w1 - t_w
    x_end = x_out + wysieg
    H = H or odl_ciecia(x_out)
    L = L or odl_ciecia(grubosc(dach))
    ob = []
    for k, (a, b, w) in enumerate(st):
        ob.append(_obsz(box(a, -H, b, 0.0 if k <= ks else y_w0), w))
    for y0, y1, w in _stos(pod, 0.0, -1):
        ob.append(_obsz(box(-L, y0, 0.0, y1), w))
    ob.append(_obsz(box(-L, 0.0, x_s1, t), plyta, "płyta stropodachu"))
    for y0, y1, w in _stos(list(reversed(nad)), t, +1):
        ob.append(_obsz(box(-L, y0, x_s0 - iz_w.d, y1), w))
    ob.append(_obsz(box(x_s0, t, x_s1, y_p), mat_att, "attyka"))
    if blok_attyki:
        ob.append(_obsz(box(x_s0, t, x_s1, t + blok_attyki[1]), blok_attyki[0], "blok termiczny u podstawy attyki"))
    ob.append(_obsz(box(x_s0 - iz_w.d, t, x_s0, y_p), iz_w.mat, "izolacja attyki (wewn.)"))
    x_iz_z = x_out if iz_z is None else x_s1 + iz_z.d
    mat_z = (iz_z.mat if iz_z is not None else sciana[-1].mat)
    ob.append(_obsz(box(x_s1, y_w1, x_iz_z, y_p), mat_z, "izolacja attyki (zewn.)"))
    ob.append(_obsz(box(x_s0 - iz_w.d, y_p, x_iz_z, y_cap), iz_w.mat, "izolacja korony attyki"))
    ob.append(_obsz(box(x_s1, y_w0, x_end, y_w1), mat_wsp or plyta.mat, "płyta wspornikowa (okap)"))
    if lacznik is not None:
        ob.append(_obsz(box(x_s1, y_w0, x_s1 + d_lacznika, y_w1), lacznik))
    S = S_STREFY
    ramka = box(-L, -H, max(x_end, x_iz_z) + S, y_cap + S)
    strefy = strefy_z_dopelnienia(ob, ramka, [((-L / 2, -H / 2), _nas("pomieszczenie", ti, "wewn")),
                                              ((x_end + S / 2, -H / 2), _nas("zewnętrze", te, "zewn"))])
    fl = [ElementFlankujacy("ściana", ("i", "e"), H + y_top, H - t_suf, warstwy=list(sciana), l_oi=H),
          ElementFlankujacy("stropodach", ("i", "e"), L + x_out, L, warstwy=list(dach), Rsi=RSI_GORA, l_oi=L)]
    x_iw = x_s0 - iz_w.d
    linie = [
        _ln("paro", [(-L, t + 0.001), (x_s0 - 0.002, t + 0.001), (x_s0 - 0.002, y_top + 0.05)],
            "paroizolacja na płycie wywinięta na attykę ponad izolację dachu (szczelność)"),
        _ln("hydro", [(-L, y_top), (x_iw, y_top), (x_iw, y_cap), (x_iz_z, y_cap)],
            f"hydroizolacja wywinięta na attykę i koronę — {h_nad_pokryciem * 100:.0f} cm ponad pokrycie "
            f"({'≥' if h_nad_pokryciem >= 0.15 else '< WYMAGANE'} 15 cm)"),
        _ln("hydro", [(x_iz_z + 0.004, y_w1 + 0.15), (x_iz_z + 0.004, y_w1 + 0.004), (x_end, y_w1 + 0.004)],
            "membrana okapu wywinięta na izolację attyki ≥ 15 cm"),
        _ln("obrobka", [(x_iw - 0.03, y_cap - 0.07), (x_iw - 0.03, y_cap + 0.01), (x_iz_z + 0.035, y_cap + 0.02),
                        (x_iz_z + 0.035, y_cap - 0.05)], "obróbka korony attyki: spadek ≥ 5 % do dachu, okapniki"),
        _ln("obrobka", [(x_end - 0.10, y_w1 + 0.006), (x_end + 0.03, y_w1 + 0.006), (x_end + 0.03, y_w0 + 0.02),
                        (x_end + 0.045, y_w0)], "obróbka czoła okapu z okapnikiem"),
        _ln("woda", [(x_iw - 0.08, y_top + 0.04), (x_iw - min(0.6, 0.8 * L), y_top + 0.04)],
            "spadek dachu ≥ 2 % do wpustów; przelew awaryjny w attyce (χ)"),
    ]
    return Wezel(id, nazwa or "Attyka w licu ściany z okapem stropodachu (łącznik termoizolacyjny)", "attyka", ob,
                 strefy, fl, przekroj="pionowy", linie=linie, punkty={"naroże sufit–ściana": (0.0, -t_suf)},
                 widok=(-min(L, 1.0), -min(H, 1.0), x_end + 0.1, y_cap + 0.1), psi_domyslne="R_attyka",
                 dane={"warstwy ściany": dane_warstw(sciana), "warstwy dachu": dane_warstw(dach),
                       "attyka": dane_warstw(attyka) + [["wys. nad pokryciem", h_nad_pokryciem]],
                       "okap": f"t = {t_w} m, wierzch {dy_wsp:+.2f} m wzgl. płyty, wysięg {wysieg} m",
                       "łącznik": (f"{lacznik.nazwa}: λ_eq = {lacznik.lam}, d = {d_lacznika} m — {lacznik.zrodlo}"
                                   if lacznik else "brak")})


# ==================================================================================================
# C. Płyta ciągła nad przegrodą pionową (dom–garaż, ściana wyższej kondygnacji, ściana pod stropem nad powietrzem)
# ==================================================================================================
def wezel_przegroda_w_linii(sciana_dol: Sequence[Warstwa], t_plyty: float, mat_plyty: Material,
                            gora_lewa: tuple, gora_prawa: tuple, dol_lewa: tuple, dol_prawa: tuple,
                            sciana_gora: Sequence[Warstwa] | None = None, t_plyty_prawa: float | None = None,
                            theta_u: float | None = None, b_u: float = 0.8, H: float | None = None,
                            L: float | None = None, theta_i: float | None = None, theta_e: float | None = None,
                            id: str = "WZ-L", nazwa: str = "Płyta ciągła nad przegrodą pionową",
                            typ: str = "polaczenie_nieogrz") -> Wezel:
    """Przekrój pionowy przez płytę ciągłą nad ścianą `sciana_dol` (lico lewe x = 0; warstwy od lewej).
    gora_lewa / gora_prawa: ('wewn', warstwy podłogi) | ('zewn', warstwy dachu od góry) — nad płytą;
    dol_lewa / dol_prawa: (rodzaj 'wewn'|'nieogrz'|'zewn', warstwy sufitu od płyty w dół[, szerokość pasa]) — pod płytą;
    sciana_gora — ściana na płycie w tej samej linii (lico lewe x = 0), rozdziela strefy nad płytą; bez niej obie
    strony nad płytą muszą być tego samego rodzaju. Płyta po prawej może mieć inną grubość (wierzch wspólny)."""
    ti, te = _temperatury(theta_i, theta_e)
    tu = _theta_u(ti, te, theta_u, b_u)
    th = {"wewn": ti, "zewn": te, "nieogrz": tu}
    t = t_plyty
    t_p = t_plyty_prawa or t
    st_d = _stos(sciana_dol, 0.0)
    D_d = st_d[-1][1]
    st_g = _stos(sciana_gora, 0.0) if sciana_gora else []
    D_g = st_g[-1][1] if st_g else 0.0
    kg = indeks_konstrukcyjnej(sciana_gora) if sciana_gora else 0
    def _gora(spec):
        return spec[0], (list(spec[1]) if spec[0] == "wewn" else _bez_went_dach(spec[1]))
    gl, gp = _gora(gora_lewa), _gora(gora_prawa)
    def _dol(spec):
        rodz, w = spec[0], list(spec[1]) if len(spec) > 1 else []
        w = _bez_went_sufit(w) if rodz == "zewn" else w
        return rodz, w, (spec[2] if len(spec) > 2 else None)
    dl, dp = _dol(dol_lewa), _dol(dol_prawa)
    t_gl, t_gp = grubosc(gl[1]), grubosc(gp[1])
    t_dl, t_dp = grubosc(dl[1]), grubosc(dp[1])
    dmax = max(D_d, D_g)
    H = H or odl_ciecia(dmax)
    L = L or odl_ciecia(max(t + t_gl + t_dl, t_p + t_gp + t_dp))
    L_p = L + (dp[2] or 0.0)
    y_bl, y_bp = 0.0, t - t_p          # spód płyty lewej / prawej (wierzch wspólny y = t)
    ob = []
    # warstwy ściany dolnej po prawej stronie ocieplenia (wyprawa) kończą się na spodzie ocieplenia sufitu
    kd = indeks_konstrukcyjnej(sciana_dol)
    iz = max([k for k in range(kd + 1, len(st_d)) if st_d[k][2].mat.lam < 0.06], default=None)
    x_dp0 = st_d[iz][1] if (iz is not None and dp[1]) else D_d
    for k, (a, b, w) in enumerate(st_d):
        y_g = (y_bp - t_dp) if (iz is not None and k > iz and dp[1]) else 0.0
        ob.append(_obsz(box(a, -H, b, y_g), w))
    for y0, y1, w in _stos(dl[1], y_bl, -1):
        ob.append(_obsz(box(-L, y0, 0.0, y1), w))
    x_dp1 = D_d + dp[2] if dp[2] else D_d + L_p
    for y0, y1, w in _stos(dp[1], y_bp, -1):
        ob.append(_obsz(box(x_dp0, y0, x_dp1, y1), w))
    ob.append(_obsz(box(-L, y_bl, D_d if t_p != t else D_d + L_p, t), mat_plyty, "płyta"))
    if t_p != t:
        ob.append(_obsz(box(min(x_dp0, D_d), y_bp, D_d + L_p, t), mat_plyty, "płyta (strona prawa)"))
    # ściana górna: warstwy za ociepleniem (wyprawa) zaczynają się nad warstwami dachu po prawej (w strefie dachu
    # ocieplenie ściany styka się z ociepleniem dachu; hydroizolacja wywinięta na ścianę — linia rysunku)
    iz_g = None
    if sciana_gora:
        iz_g = max([k for k in range(kg + 1, len(st_g)) if st_g[k][2].mat.lam < 0.06], default=None)
    x_gp0 = (st_g[iz_g][1] if (iz_g is not None and gp[0] == "zewn") else D_g) if sciana_gora else 0.0
    for y0, y1, w in _stos(list(reversed(gl[1])), t, +1):
        ob.append(_obsz(box(-L, y0, 0.0, y1), w))
    for y0, y1, w in _stos(list(reversed(gp[1])), t, +1):
        ob.append(_obsz(box(x_gp0, y0, D_d + L_p, y1), w))
    if sciana_gora:
        for k, (a, b, w) in enumerate(st_g):
            y_s = t + t_gp if (iz_g is not None and k > iz_g and gp[0] == "zewn") else t
            ob.append(_obsz(box(a, y_s, b, t + max(t_gl, t_gp) + H), w))
    S = S_STREFY
    y_top = t + max(t_gl, t_gp) + H
    ramka = box(-L, -H, D_d + L_p, y_top)
    nas, grp = [], {}
    def seed(xy, rodz, nm):
        g = GRUPY[rodz]
        nas.append((xy, _nas(nm, th[rodz], rodz, g)))
        grp[nm] = g
    seed((-L / 2, -H / 2), dl[0], "dół lewa")
    seed((D_d + L_p / 2, -H / 2), dp[0], "dół prawa")
    seed((-L / 2, y_top - S / 2), gl[0], "góra lewa")
    if sciana_gora or gp[0] != gl[0]:
        seed((D_d + L_p - S / 2, y_top - S / 2), gp[0], "góra prawa")
    strefy = strefy_z_dopelnienia(ob, ramka, nas)
    fl = _flank_linia(sciana_dol, sciana_gora, t, t_p, mat_plyty, gl, gp, dl, dp, H, L, L_p, D_d, D_g, grp)
    linie = _linie_linia(gl, gp, dl, dp, t, D_d, D_g, L, L_p, sciana_gora, t_gp)
    return Wezel(id, nazwa, typ, ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"naroże dół lewa": (0.0, -t_dl)},
                 widok=(-min(L, 1.0), -min(H, 1.0), D_d + min(L_p, 1.2), t + max(t_gl, t_gp) + min(H, 0.8)),
                 dane={"ściana dolna (od lewej)": dane_warstw(sciana_dol),
                       "ściana górna (od lewej)": dane_warstw(sciana_gora or []),
                       "płyta": f"{mat_plyty.kod}, t = {t} m" + (f" (prawa {t_p} m)" if t_p != t else ""),
                       "nad płytą L/P": f"{gl[0]} / {gp[0]}", "pod płytą L/P": f"{dl[0]} / {dp[0]}"
                                                                           + (f" (pas {dp[2]} m)" if dp[2] else ""),
                       "warstwy nad płytą L": dane_warstw(gl[1]), "warstwy nad płytą P": dane_warstw(gp[1]),
                       "warstwy pod płytą L": dane_warstw(dl[1]), "warstwy pod płytą P": dane_warstw(dp[1]),
                       "θ_u": f"{tu:.1f} °C" + (" (zadana)" if theta_u is not None else f" z b_u = {b_u} [ZAŁ]")},
                 uwagi=["Grupy stref: i — ogrzewane, u — nieogrzewane, e — zewnętrze; ψ dla każdej pary grup "
                        "z elementami flankującymi (PN-EN ISO 10211, więcej niż dwie temperatury)."])


def _flank_linia(sciana_dol, sciana_gora, t, t_p, mat_plyty, gl, gp, dl, dp, H, L, L_p, D_d, D_g, grp) -> list:
    """Elementy flankujące węzła `wezel_przegroda_w_linii` dla par różnych grup stref."""
    g_dl, g_dp, g_gl = grp["dół lewa"], grp["dół prawa"], grp["góra lewa"]
    g_gp = grp.get("góra prawa", g_gl)
    t_gl, t_gp, t_dl = grosz(gl[1]), grosz(gp[1]), grosz(dl[1])
    fl = []
    if g_dl != g_dp:            # ściana dolna
        rs = RSI_POZIOMO if "e" not in (g_dl, g_dp) else 0.04
        l_oi = H + t + t_gl if gl[0] == "wewn" else H
        fl.append(ElementFlankujacy("ściana dolna", (g_dl, g_dp), H + t / 2, H - t_dl, warstwy=list(sciana_dol),
                                    Rse=rs, l_oi=l_oi))
    if sciana_gora and g_gl != g_gp:
        h_s = max(t_gl, t_gp) + H
        rs = RSI_POZIOMO if "e" not in (g_gl, g_gp) else 0.04
        fl.append(ElementFlankujacy("ściana górna", (g_gl, g_gp), h_s - t_gp, h_s - t_gl, warstwy=list(sciana_gora),
                                    Rse=rs, l_oi=h_s - t_gl))
    def poziomy(nazwa, gora, dol, tt, gg, gd, l_e, l_i):
        if gg == gd:
            return
        w = list(gora[1] if gora[0] != "wewn" else gora[1]) + [Warstwa(mat_plyty, tt, True)] + list(dol[1] if not dol[2] else [])
        # kierunek strumienia: od ciepłej strony — w górę, gdy ciepło pod płytą
        cieplo_pod = {"i": 2, "u": 1, "e": 0}[gd] > {"i": 2, "u": 1, "e": 0}[gg]
        rsi = RSI_GORA if cieplo_pod else RSI_DOL
        rse = 0.04 if "e" in (gg, gd) else rsi
        fl.append(ElementFlankujacy(nazwa, (gd, gg), l_e, l_i, warstwy=w, Rsi=rsi, Rse=rse, l_oi=l_i))
    poziomy("przegroda pozioma lewa", gl, dl, t, g_gl, g_dl, L + (D_d / 2), L)
    poziomy("przegroda pozioma prawa", gp, dp, t_p, g_gp, g_dp, L_p + (D_d / 2), L_p)
    return fl


def grosz(w) -> float:
    return grubosc(w)


def _linie_linia(gl, gp, dl, dp, t, D_d, D_g, L, L_p, sciana_gora, t_gp) -> list:
    lin = []
    if gp[0] == "zewn" and sciana_gora:
        h = t + t_gp
        lin.append(_ln("hydro", [(D_d + L_p, h), (D_g + 0.004, h), (D_g + 0.004, h + 0.15 + 0.03)],
                       "hydroizolacja dachu wywinięta na ścianę ≥ 15 cm ponad warstwę wierzchnią (substrat / żwir)"))
        lin.append(_ln("woda", [(D_g + 0.6, h + 0.04), (D_g + min(1.1, L_p - 0.05), h + 0.04)],
                       "spadek dachu ≥ 2 % od ściany; opaska żwirowa ≥ 0,5 m przy ścianie"))
    if gl[0] == "zewn" and gp[0] == "zewn" and not sciana_gora:
        h = t + grosz(gl[1])
        lin.append(_ln("hydro", [(-L, h), (D_d + L_p, h)], "hydroizolacja dachu ciągła nad ścianą"))
    if "nieogrz" in (dl[0], dp[0]):
        lin.append(_ln("paro", [(-L, -grosz(dl[1]) - 0.002), (-0.002, -grosz(dl[1]) - 0.002), (-0.002, -1.0)],
                       "tynk / szczelność powietrzna i gazowa od strony garażu (WT § 106)"))
    return lin


# ==================================================================================================
# D. Ściana dom–garaż na ciągłej płycie fundamentowej
# ==================================================================================================
def wezel_garaz_plyta(sciana: Sequence[Warstwa], podloga_lewa: Sequence[Warstwa], podloga_prawa: Sequence[Warstwa],
                      theta_u: float | None = None, b_u: float = 0.8, h_gruntu: float = 1.0,
                      blok: tuple[Material, float] | None = None, H: float | None = None,
                      L: float | None = None, theta_i: float | None = None, theta_e: float | None = None,
                      id: str = "WZ-GP", nazwa: str = "Ściana dom–garaż na ciągłej płycie fundamentowej",
                      uskok: float = 0.0, zebro: tuple[float, float] | None = None, x_os: float | None = None,
                      przerwa: tuple[Material, float] | None = None) -> Wezel:
    """Ściana (lico lewe = dom x = 0, prawe = garaż) na płycie fundamentowej ciągłej pod domem i garażem.
    podloga_lewa / prawa — warstwy podłóg od góry z płytą (konstrukcyjna) i warstwami pod płytą (XPS, podsypka).
    ``uskok`` — obniżenie płyty garażu względem płyty domu [m] (uskok w osi warstwy konstrukcyjnej ściany ``x_os``; beton pod
    ściną do jej lica od garażu), ``zebro`` — (szerokość, głębokość spodu poniżej wierzchu płyty domu) żebra pod ścianą, osiowo
    (wydanie — weryfikacja V2 N-6: geometria węzła = geometria modelu PF1/PF2 + ZF). Wierzch posadzki domu y = 0. Pod podsypką grunt (λ = 2,0) grubości h_gruntu, dół i boki adiabatyczne [ZAŁ]:
    węzeł wewnętrzny daleko od krawędzi płyty — ψ_iu (dom → garaż) z przepływu przez płytę pod ścianą; wymiana
    z gruntem ujęta w U podłóg (PN-EN ISO 13370) poza węzłem."""
    ti, te = _temperatury(theta_i, theta_e)
    tu = _theta_u(ti, te, theta_u, b_u)
    st = _stos(sciana, 0.0)
    D = st[-1][1]
    kl, kp = indeks_konstrukcyjnej(podloga_lewa), indeks_konstrukcyjnej(podloga_prawa)
    y_w = -grubosc(podloga_lewa[:kl])            # wierzch płyty
    t_pl = podloga_lewa[kl].d
    H = H or odl_ciecia(D)
    L = L or odl_ciecia(grubosc(podloga_lewa))
    ob = []
    for y0, y1, w in _stos(podloga_lewa[:kl], 0.0, -1):
        ob.append(_obsz(box(-L, y0, 0.0, y1), w))
    if uskok <= 1e-6 and zebro is None:
        y_pp = y_w + grosz(podloga_prawa[:kp])
        for y0, y1, w in _stos(podloga_prawa[:kp], y_pp, -1):
            ob.append(_obsz(box(D, y0, D + L, y1), w))
        ob.append(_obsz(box(-L, y_w - t_pl, D + L, y_w), podloga_lewa[kl], "płyta fundamentowa"))
        y = y_w - t_pl
        for w in podloga_lewa[kl + 1:]:
            if w.d < 0.001:
                continue
            ob.append(_obsz(box(-L, y - w.d, D + L, y), w))
            y -= w.d
        ob.append(_obsz(box(-L, y - h_gruntu, D + L, y), MATERIALY_DOMYSLNE["GRUNT"], "grunt"))
    else:
        from shapely.ops import unary_union as _uu
        kk = indeks_konstrukcyjnej(sciana)
        xo = x_os if x_os is not None else (st[kk][0] + st[kk][1]) / 2
        yg = y_w - uskok                                                  # wierzch płyty garażu
        y_pp = yg + grosz(podloga_prawa[:kp])
        for y0, y1, w in _stos(podloga_prawa[:kp], y_pp, -1):
            ob.append(_obsz(box(D, y0, D + L, y1), w))
        beton = [box(-L, y_w - t_pl, xo, y_w), box(xo, yg - t_pl, D + L, yg)]
        if uskok > 1e-6:
            beton.append(box(xo, yg, D, y_w))                            # beton pod ścianą do lica od garażu (uskok)
        if zebro is not None:
            bz, gz = zebro
            beton.append(box(xo - bz / 2, y_w - gz, xo + bz / 2, y_w))
        B = _uu(beton)
        if przerwa is not None:          # wariant: przerwa termiczna płyty garażu przy żebrze/uskoku (izolacja pionowa na grubości PF2)
            xb = max(D, xo + (zebro[0] / 2 if zebro else 0.0))
            pz = box(xb, yg - t_pl, xb + przerwa[1], yg)
            B = B.difference(pz)
            ob.append(_obsz(pz, przerwa[0], "przerwa termiczna płyty (wariant)"))
        ob.append(_obsz(B, podloga_lewa[kl], "płyta fundamentowa z uskokiem" + (" i żebrem" if zebro else "")))
        pod = [w for w in podloga_lewa[kl + 1:] if w.d >= 0.001]
        yl, yr = y_w - t_pl, yg - t_pl
        for w in pod:
            for g in (box(-L, yl - w.d, xo, yl), box(xo, yr - w.d, D + L, yr)):
                g = g.difference(B)
                if not g.is_empty and g.area > 1e-8:
                    ob.append(_obsz(g, w))
            yl, yr = yl - w.d, yr - w.d
        y = min(yl, yr, y_w - (zebro[1] if zebro else 0.0))
        gr = box(-L, y - h_gruntu, D + L, max(yl, yr)).difference(_uu([o.wielobok for o in ob]))
        ob.append(_obsz(gr, MATERIALY_DOMYSLNE["GRUNT"], "grunt"))
    for a, b, w in st:
        ob.append(_obsz(box(a, y_w, b, H), w))
    if blok:            # blok termoizolacyjny w pierwszej warstwie muru (wariant)
        kk = indeks_konstrukcyjnej(sciana)
        ob.append(_obsz(box(st[kk][0], y_w, st[kk][1], y_w + blok[1]), blok[0], "blok termoizolacyjny"))
    S = S_STREFY
    ramka = box(-L, y - h_gruntu, D + L, H)
    strefy = strefy_z_dopelnienia(ob, ramka, [((-L / 2, H / 2), _nas("dom (ogrzewany)", ti, "wewn")),
                                              ((D + L / 2, H / 2), _nas("garaż nieogrzewany", tu, "nieogrz"))])
    fl = [ElementFlankujacy("ściana dom–garaż (od posadzki domu)", ("i", "u"), H, H, warstwy=list(sciana),
                            Rse=RSI_POZIOMO)]
    linie = [_ln("przeciwwilg", [(-L, y_w + 0.003), (D + L, y_w + 0.003)],
                 "izolacja przeciwwilgociowa/przeciwradonowa na płycie — ciągła pod ścianą"),
             _ln("paro", [(-0.002, H), (-0.002, 0.0)], "tynk wewnętrzny do posadzki — szczelność powietrzna"),
             _ln("tasma_zewn", [(D + 0.002, y_pp + 0.01), (D + 0.002, 0.30)],
                 "garaż: uszczelnienie styku ściana–posadzka (szczelność gazowa, WT § 106), cokolik")]
    return Wezel(id, nazwa, "garaz", ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"naroże ściana–posadzka (dom)": (0.0, 0.0)},
                 widok=(-min(L, 1.0), y - 0.3, D + min(L, 1.0), 0.9),
                 dane={"ściana (od domu)": dane_warstw(sciana), "podłoga domu": dane_warstw(podloga_lewa),
                       "posadzka garażu": dane_warstw(podloga_prawa),
                       "grunt": f"λ = 2,0, warstwa {h_gruntu} m pod podsypką, dół adiabatyczny [ZAŁ]",
                       "θ_u": f"{tu:.1f} °C" + (" (zadana)" if theta_u is not None else f" z b_u = {b_u} [ZAŁ]")},
                 uwagi=["ψ_iu = L_2D,iu − U_ściany·h (podłogi po obu stronach nie wymieniają ciepła z gruntem w "
                        "modelu węzła — dół adiabatyczny); strata do garażu wchodzi do H_U = H_iu·b_u (PN-EN ISO 13789)."])
