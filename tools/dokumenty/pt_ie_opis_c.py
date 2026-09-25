"""PT-4 IE — część opisowa C: ochrona przeciwporażeniowa i przeciwprzepięciowa, bilans mocy (§ 23 pkt 11 lit. a,
§ 23 pkt 8 lit. b), zestawienie wyników i pełne obliczenia, dane ppoż. i PWP (§ 23 pkt 10, WT § 183 ust. 2–4),
wyroby i parametry wymagane, próby i odbiory, braki danych. Liczby wyłącznie z ``DanePTIE``."""
from __future__ import annotations

from pt_ie_dane import KAT_ZRODLA, L, DanePTIE, Opis
from pt_is_opis_b import OPS, wstaw_raport

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


def _e(D: DanePTIE, k: str, d=None):
    return D.v("elektryka", k, d)


def wiersz(x, parametr: str | None = None, miejsca: int = 2) -> dict:
    """Wiersz tabeli wyników z obiektu ``Warunek`` biblioteki obliczeń."""
    lim = x.limit
    lim_t = (f"{L(lim[0], miejsca)}–{L(lim[1], miejsca)}" if isinstance(lim, (list, tuple))
             else L(lim, miejsca) if isinstance(lim, (int, float)) else str(lim or ""))
    return dict(parametr=parametr or x.opis, wartosc=x.wartosc, jedn=x.jedn or "", miejsca=miejsca,
                wymaganie=f"{OPS.get(x.op, x.op)} {lim_t} {x.jedn or ''}".strip() if x.op != "info" else "—",
                podstawa=f"{x.podstawa} [{x.id}]" if x.id else x.podstawa, spelnia=x.ok)


def _w(D: DanePTIE, modul: str, fragment: str):
    return next((x for x in D.warunki(modul) if fragment in x.opis), None)


def rozdz_ochrona(o: Opis, D: DanePTIE):
    """9. Ochrona przeciwporażeniowa i przeciwprzepięciowa."""
    ob, par, spd = D.obw.obwody, D.obw.par, D.obw.spd
    kr = min(ob, key=lambda x: x.I_k1 / x.I_a)
    zs = max(ob, key=lambda x: x.Z_s)
    rcd = D.kategoria_rcd
    o.rozdzial("Ochrona przeciwporażeniowa i przeciwprzepięciowa",
               podstawa="WT § 183 ust. 1 pkt 3, 10; PN-HD 60364-4-41, -4-443; W-181, W-182, W-186", nowa_strona=True)
    o.tekst(f"""
    **Ochrona podstawowa** — izolacja części czynnych, obudowy i osłony (PN-HD 60364-4-41 zał. A).
    **Ochrona przy uszkodzeniu** — samoczynne wyłączenie zasilania w układzie TN-S: dla obwodów odbiorczych
    230 V czas wyłączenia ≤ {L(_e(D, 'czas_wylaczenia_TN_230V_max', par.t_wyl), 1)} s (tabl. 41.1), sprawdzony
    warunkiem I_k1 ≥ I_a (I_a — prąd zadziałania członu zwarciowego wyłącznika: 5·I_n dla B, 10·I_n dla C).
    Najmniejszy zapas: obwód {kr.odb.id} — I_k1 = {L(kr.I_k1, 0)} A ≥ I_a = {L(kr.I_a, 0)} A
    (I_k1/I_a = {L(kr.I_k1 / kr.I_a, 2)}); największa impedancja pętli zwarcia: obwód {zs.odb.id} —
    Z_s = {L(zs.Z_s, 3)} Ω (temperatura żył 70 °C, c_min = 0,95). **Ochrona uzupełniająca** — urządzenia
    różnicowoprądowe I_∆n ≤ {L(_e(D, 'RCD_IDn_max'), 0)} mA w obwodach gniazd ≤ {L(_e(D, 'RCD_gniazda_In_do'), 0)} A,
    oświetlenia, łazienek i urządzeń na zewnątrz (411.3.3–411.3.4, W-181); typ AC niedopuszczalny.
    Zastosowane rodzaje: {'; '.join(f'{k} — {len(v)} {"obwód" if len(v) == 1 else "obwody" if len(v) < 5 else "obwodów"}' for k, v in rcd.items())}.
    Połączenia wyrównawcze główne — rozdz. 8.3.

    **Selektywność** (WT § 183 ust. 1 pkt 5): przeciążeniowa zapewniona (I_n zabezpieczenia przedlicznikowego / I_n
    obwodu ≥ 1,6); zwarciowa — częściowa, do granicy wynikającej z tabel producenta aparatów (zestawienie w obliczeniach
    obwodów); aparat główny RG — rozłącznik (nie wyzwala przy zwarciu).

    **Ochrona przed przepięciami** (WT § 183 ust. 1 pkt 10 — obowiązkowa; PN-HD 60364-4-443): krytyczna długość linii
    CRL = {L(spd['CRL'], 0)} < {L(_e(D, 'CRL_prog'), 0)} (f_env = {L(spd['f_env'], 0)}, N_g = {L(spd['Ng'], 1)}) —
    ochrona wymagana także z warunku normy. W RG: {spd['RG']}. Dalej: {spd['DC']}; {spd['tele']}; {spd['T3']}.
    Kategorie wytrzymałości udarowej: złącze — IV (6 kV), RG i oprzewodowanie — III (4 kV), odbiorniki — II (2,5 kV),
    elektronika chroniona — I (1,5 kV); U_p ochronników w RG ≤ {L(_e(D, 'SPD_Up_max'), 1)} kV (W-186).
    """)


def rozdz_bilans(o: Opis, D: DanePTIE):
    """10. Bilans mocy (§ 23 pkt 11 lit. a) i moce elektryczne urządzeń HVAC (§ 23 pkt 8 lit. b)."""
    b = D.bil
    o.rozdzial("Bilans mocy", podstawa="§ 23 pkt 11 lit. a RPB; § 23 pkt 8 lit. b RPB; W-192", nowa_strona=True)
    grp: dict = {}
    for x in b.odbiorniki:
        if x.generacja:
            continue
        g = grp.setdefault(x.grupa, {"Grupa odbiorników": x.grupa, "Obwody": [], "P_i [kW]": 0.0, "k_j": x.k_j,
                                     "P_s [kW]": 0.0, "DLM": "—"})
        g["Obwody"].append(x.id)
        g["P_i [kW]"] += x.P
        g["P_s [kW]"] += x.P_s
        if x.sterowany:
            g["DLM"] = "tak"
    wiersze = [dict(v, Obwody=", ".join(v["Obwody"])) for v in grp.values()]
    wiersze.append({"Grupa odbiorników": "Razem (bez zarządzania mocą)", "Obwody": "", "P_i [kW]": b.P_inst,
                    "k_j": None, "P_s [kW]": b.P_s_bez, "DLM": "", "_klasa": "suma"})
    o.tekst(f"""
    Bilans obejmuje urządzenia elektryczne stanowiące stałe wyposażenie budowlano-instalacyjne budynku; urządzeń
    technologicznych nie ma (budynek mieszkalny jednorodzinny). Moc szczytową wyznaczono ze współczynników
    jednoczesności k_j [ZAŁ] dla grup odbiorników; mikroinstalacja PV (generacja) nie pomniejsza bilansu poboru.
    """)
    o.tabela(wiersze, tytul="Bilans mocy — grupy odbiorników", formaty={"P_i [kW]": 2, "k_j": 2, "P_s [kW]": 2},
             zrodlo="lamela.obliczenia.elektryka.bilans (odbiorniki z modelu i z doboru urządzeń PT-3 IS)")
    hvac = [x for x in b.odbiorniki if x.grupa in ("pc", "grzalka", "went", "sterowanie")]
    o.tabela([{"Urządzenie": x.nazwa, "Obwód": x.id, "P_el [kW]": x.P, "Fazy": x.fazy} for x in hvac],
             tytul="Moc elektryczna urządzeń ogrzewczych i wentylacyjnych (§ 23 pkt 8 lit. b)",
             formaty={"P_el [kW]": 2}, suma=["P_el [kW]"], zrodlo="dobór urządzeń — PT-3 IS; bilans — PT-4 IE")
    o.tekst(f"""
    **Moc szczytowa bez zarządzania mocą** P_s = {L(b.P_s_bez, 1)} kW > moc przyłączeniowa {L(b.P_przyl, 0)} kW —
    **wymagane dynamiczne zarządzanie mocą (DLM)**: ograniczenie prądu ładowania EV i blokada grzałki rezerwowej
    przy przekroczeniu mocy (pomiar prądów faz za licznikiem, sterownik DLM w RG). **Moc szczytowa z DLM**
    P_s,DLM = {L(b.P_s_dlm, 1)} kW ≤ {L(b.P_przyl, 0)} kW; prąd szczytowy I_B = {L(b.I_B, 1)} A ≤
    {L(b.I_zab, 0)} A (zabezpieczenie przedlicznikowe). Kontrolnie wg N SEP-E-002 (30 kVA + ogrzewanie elektryczne):
    {L(b.sep, 1)} kW [NZW]. Moc przyłączeniowa {L(b.P_przyl, 0)} kW ≤ {L(_e(D, 'grupa_przylaczeniowa_V_moc_max'), 0)} kW
    (grupa V) — do wniosku o warunki przyłączenia.
    """)
    o.tabela([{"Faza": k, "P_s [kW]": v, "I [A]": v * 1000 / (230 * b.par.cosphi_sr)} for k, v in b.fazy.items()],
             tytul="Podział mocy szczytowej (z DLM) na fazy", formaty={"P_s [kW]": 2, "I [A]": 1},
             uwagi=f"Asymetria (max − min)/średnia = {L(100 * b.asymetria, 1)} %; cos φ = {L(b.par.cosphi_sr, 2)}.")
