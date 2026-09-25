"""PAB — rozdziały 10–11 (RPB § 20 ust. 1 pkt 10–11): systemy alternatywne i automatyczna regulacja temperatury."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from lamela.dokumenty import do_uzup, liczba as L  # noqa: E402
from lamela.dokumenty.znaczniki import DANE_PRZYKLADOWE, ZAL  # noqa: E402

from pab_opis_a import ok, tyt  # noqa: E402

NOSNIKI = {"woda": None, "kan_sanit": None, "tele": None, "en": "energia elektryczna z sieci nN",
           "gaz": "gaz ziemny z sieci gazowej", "cieplo": "ciepło sieciowe"}


def _wykres_ep(wyniki, ep_max):
    fig, ax = plt.subplots(figsize=(6.3, 2.3))
    naz = [w.system.nazwa.split(":")[0] for w in wyniki][::-1]
    val = [w.EP for w in wyniki][::-1]
    kol = ["#4d7f5e" if w.spelnia else "#b5543c" for w in wyniki][::-1]
    ax.barh(naz, val, color=kol, height=0.55)
    ax.axvline(ep_max, color="#222", lw=1.0, ls="--")
    ax.text(ep_max, len(naz) - 0.45, f" EP_max = {L(ep_max, 0)}", fontsize=7, va="bottom")
    for i, v in enumerate(val):
        ax.text(v + 1, i, L(v, 1), va="center", fontsize=7)
    ax.set_xlabel("EP [kWh/(m²·rok)]", fontsize=8)
    ax.tick_params(labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


def r10(pab, D, d):
    alt, ep, pv = D.R["ep_alt"], D.ep, D.Wd["pv"]
    wo, og = D.Wd["woda"], D.Wd["ogrzewanie"]
    ep_max = D.v("energia", "EP_max")
    nos = [NOSNIKI.get(b) for b, _o in D.nosniki if NOSNIKI.get(b)]
    base = next((w for w in alt if w.system.nosnik_H == "gaz"), None)
    wyb = min((w for w in alt if w.spelnia), key=lambda w: (w.EP, w.koszt_zl), default=None)
    en = D.B.get("energia") or {}
    pab.rozdzial(tyt("Analiza możliwości racjonalnego wykorzystania wysoce wydajnych systemów alternatywnych "
                     "zaopatrzenia w energię i ciepło", 10))
    pab.markdown(f"""
    ## Roczne zapotrzebowanie na energię użytkową (lit. a)

    Obliczenia wg metodologii charakterystyki energetycznej (Dz.U. 2015 poz. 376 ze zm.) modułem
    `lamela.obliczenia.energia` na danych modelu: powierzchnia o regulowanej temperaturze A_{{f}} = {L(ep.A_f, 2)} m²;
    energia użytkowa na ogrzewanie i wentylację Q_{{H,nd}} = {L(ep.Q_H_nd, 0)} kWh/rok, na przygotowanie c.w.u.
    Q_{{W,nd}} = {L(ep.Q_W_nd, 0)} kWh/rok; wskaźnik EU = {L(ep.EU, 1)} kWh/(m²·rok). Mostki cieplne — wartości Ψ
    z symulacji PN-EN ISO 10211 (H_{{TB}} = {L(D.ob.H_TB, 2)} W/K); szczelność n_{{50}} = {L(en.get('n50'), 1)} h⁻¹ (cel
    projektowy, próba szczelności PN-EN ISO 9972 przed odbiorem).

    ## Dostępne nośniki energii (lit. b)

    Na działce i w drodze dostępne są: {', '.join(nos) or '—'}; energia promieniowania słonecznego (dachy płaskie) oraz
    energia otoczenia (powietrze zewnętrzne — pompa ciepła). Sieć ciepłownicza nie występuje (dane uzbrojenia działki
    {DANE_PRZYKLADOWE}; oświadczenie projektanta z art. 33 ust. 2 pkt 10 PB — element „Załączniki”).

    ## Systemy do analizy porównawczej (lit. c) i obliczenia (lit. d)

    System konwencjonalny: **{base.system.nazwa if base else '—'}**; system alternatywny: **{alt[0].system.nazwa}**
    (pompa ciepła powietrze–woda, wentylacja mechaniczna z odzyskiem ciepła o sprawności
    η = {L(100 * D.went.eta, 0)} %, instalacja fotowoltaiczna {pv['n_modulow']} × moduł = {L(pv['P_kWp'], 2)} kWp,
    magazyn ciepła). Wariantami kontrolnymi są: system alternatywny bez PV oraz pompa ciepła z wartościami domyślnymi
    metodologii. Dla każdego wariantu obliczono EU, EK, EP, emisję CO₂, udział OZE i roczny koszt energii.
    """)
    rows = [{"System": w.system.nazwa, "EK [kWh/(m²·rok)]": w.EK, "EP [kWh/(m²·rok)]": w.EP,
             f"EP ≤ {L(ep_max, 0)}": ok(w.spelnia), "E_CO2 [t/rok]": w.E_CO2_t, "U_OZE [%]": w.U_oze,
             "Koszt energii [zł/rok]": w.koszt_zl, "Nakłady [zł]": w.system.capex_zl} for w in alt]
    pab.tabela(rows, tytul="Porównanie systemów zaopatrzenia w energię (RPB § 20 ust. 1 pkt 10 lit. d)", klasa="zwarta",
               formaty={"EK [kWh/(m²·rok)]": 1, "EP [kWh/(m²·rok)]": 1, "U_OZE [%]": 0, "Koszt energii [zł/rok]": 0,
                        "Nakłady [zł]": 0}, szerokosci=[None, "16mm", "16mm", "18mm", "15mm", "14mm", "18mm", "17mm"],
               uwagi=[f"EP_max = {L(ep_max, 0)} kWh/(m²·rok) — {D.zr('energia', 'EP_max')}. Ceny energii i nakłady "
                      f"inwestycyjne — założenia orientacyjne {ZAL} (`lamela.obliczenia/dane/wyroby_przykladowe.yaml`), "
                      f"parametry urządzeń — wyroby przykładowe {DANE_PRZYKLADOWE}; nakłady obejmują tylko elementy "
                      "różniące warianty."], zrodlo="lamela.obliczenia.fizyka_energia (oblicz_wszystko → ep_alt)")
    pab.wykres(_wykres_ep(alt, ep_max), podpis="Wskaźnik EP wariantów systemu na tle wartości granicznej WT",
               szerokosc="150mm")
    plt.close("all")
    zwrot = ""
    if wyb is not None and base is not None and base is not wyb and wyb.system.capex_zl and base.system.capex_zl:
        dk = base.koszt_zl - wyb.koszt_zl
        zwrot = (f" Roczny koszt energii niższy o {L(dk, 0)} zł od systemu konwencjonalnego; prosty okres zwrotu nakładów "
                 f"dodatkowych ≈ {L((wyb.system.capex_zl - base.system.capex_zl) / dk, 1)} roku {ZAL}." if dk > 0 else
                 f" Roczny koszt energii wyższy o {L(-dk, 0)} zł od systemu konwencjonalnego.")
    wr = "; ".join(f"{w.system.nazwa}: EP = {L(w.EP, 1)} ({ok(w.spelnia)})" for w in D.R.get("ep_wrazliwosc", []))
    pab.markdown(f"""
    ## Wyniki analizy i wybór systemu (lit. e)

    Wybrano system **{wyb.system.nazwa if wyb else '—'}** — najniższy wskaźnik EP spośród wariantów spełniających
    wymaganie WT (EP = {L(wyb.EP, 1) if wyb else '—'} kWh/(m²·rok), udział OZE {L(wyb.U_oze, 0) if wyb else '—'} %).{zwrot}
    System konwencjonalny (kocioł gazowy) {'nie spełnia' if base and not base.spelnia else 'spełnia'} wymagania EP_max.
    Instalacja fotowoltaiczna: produkcja {L(pv['E_PV_kWh_a'], 0)} kWh/rok, autokonsumpcja {L(100 * pv['autokonsumpcja'], 0)} %
    (symulacja godzinowa TMY/PVGIS; `lamela.obliczenia.elektryka.pv`). Magazyn ciepła: zasobnik c.w.u.
    {wo['zasobnik_l']} dm³ ładowany w pierwszej kolejności z nadwyżek PV (sterowanie c.w.u. z PV:
    {'tak' if getattr(ep.system, 'sterowanie_cwu_pv', False) else 'nie'}), bufor instalacji grzewczej min.
    {og['bufor_l']} dm³ oraz akumulacja ciepła w masywnych stropach i jastrychach (klasa pojemności cieplnej:
    „{en.get('pojemnosc', '—')}”). Magazyn energii elektrycznej nie jest przewidywany. Wrażliwość wyniku: {wr}.
    """)


def r11(pab, D, d):
    og, en = D.W["ogrzewanie"], D.B.get("energia") or {}
    petle = og.petle or []
    pom_reg = sorted({p.pom for p in petle})
    grz = D.I.get("grzejniki") or []
    ep = D.ep
    from lamela.obliczenia.energia.ep import wyrob
    c_el = float(wyrob("ceny").get("energia_elektryczna_zl_kWh") or 0)
    C_H = ep.Q_K_H * c_el
    chl = bool(en.get("chlodzenie"))
    te = D.obc.theta_e
    tg = (D.obc.dobor or {}).get("t_graniczna")
    pab.rozdzial(tyt("Analiza technicznych i ekonomicznych możliwości automatycznej regulacji temperatury", 11))
    pab.markdown(f"""
    **Wymaganie:** instalacje ogrzewcze wyposaża się w urządzenia automatycznie regulujące temperaturę oddzielnie
    w poszczególnych pomieszczeniach (WT § 135 ust. 7); regulacja strefowa jest dopuszczalna przy braku możliwości montażu
    (ust. 8); wymaganie stosuje się, gdy jest technicznie możliwe (opinia projektanta z uprawnieniami) i ekonomicznie
    uzasadnione — okres zwrotu nakładów nie dłuższy niż 5 lat (ust. 9; W-152). Wymagania WT § 147 ust. 5–7 dotyczą
    instalacji klimatyzacji — {'dotyczą' if chl else '**nie dotyczy** (budynek bez instalacji chłodzenia; model: energia.chlodzenie)'}.

    **Możliwość techniczna:** ogrzewanie wodne płaszczyznowe zasilane z pompy ciepła, z rozdzielaczami na każdej kondygnacji
    ({len(og.rozdzielacze)} rozdzielacze) i {len(petle)} pętlami grzejnymi obsługującymi {len(pom_reg)} pomieszczeń oraz
    {len(grz)} ścianami grzewczymi w łazienkach i przy klatce schodowej. Każda pętla (grupa pętli pomieszczenia) ma siłownik
    termoelektryczny na rozdzielaczu sterowany termostatem pomieszczeniowym — **regulacja indywidualna w każdym
    pomieszczeniu ogrzewanym jest technicznie możliwa** (opinia: projektant instalacji sanitarnych
    {do_uzup('imię, nazwisko, nr uprawnień')}). Temperatura zasilania prowadzona pogodowo przez regulator pompy ciepła
    (krzywa grzewcza — rysunek poniżej): projektowo {L(og.theta_V, 1)} °C przy θ_{{e}} = {L(te, 0)} °C, obniżana liniowo do
    temperatury wewnętrznej przy granicy grzania {L(tg, 0)} °C {ZAL}.

    **Możliwość ekonomiczna:** roczne zużycie energii końcowej na ogrzewanie Q_{{K,H}} = {L(ep.Q_K_H, 0)} kWh/rok, koszt
    C_{{H}} = {L(C_H, 0)} zł/rok przy cenie {L(c_el, 2)} zł/kWh {ZAL}. Kryterium ust. 9 pkt 2: SPBT = K / (s·C_{{H}}) ≤ 5 lat,
    gdzie K — nakład na termostaty i siłowniki {do_uzup('K — oferta (PT-IS)')}, s — względna oszczędność energii na
    ogrzewanie {do_uzup('s — dane producenta systemu regulacji / PT-IS')}. Ze względu na małą bezwładność sterowania
    pojedynczych pętli, zyski słoneczne od południa (przeszklenia strefy dziennej) i zróżnicowane temperatury pomieszczeń
    przyjęto **regulację pomieszczeniową w każdym pomieszczeniu ogrzewanym** bez korzystania z odstępstwa z ust. 8–9;
    obliczenie okresu zwrotu — w PT-3 IS.
    """)
    fig, ax = plt.subplots(figsize=(4.8, 2.2))
    ti = max((float(r.temp) for r in D.m.pomieszczenia() if r.pobyt_ludzi and r.temp), default=og.theta_V)
    ax.plot([te, tg], [og.theta_V, ti], color="#2d5d8a", lw=1.6)
    ax.set_xlabel("θ_e [°C]", fontsize=8)
    ax.set_ylabel("θ_zasilania [°C]", fontsize=8)
    ax.grid(alpha=0.3)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    pab.wykres(fig, podpis="Krzywa grzewcza (regulacja pogodowa temperatury zasilania) — wartości z obliczeń ogrzewania",
               szerokosc="110mm")
    plt.close("all")
