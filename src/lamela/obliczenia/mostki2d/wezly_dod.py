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
