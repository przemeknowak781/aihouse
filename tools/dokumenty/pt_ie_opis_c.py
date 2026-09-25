"""PT-4 IE — część opisowa C: ochrona przeciwporażeniowa i przeciwprzepięciowa, bilans mocy (§ 23 pkt 11 lit. a,
§ 23 pkt 8 lit. b), zestawienie wyników i pełne obliczenia, dane ppoż. i PWP (§ 23 pkt 10, WT § 183 ust. 2–4),
wyroby i parametry wymagane, próby i odbiory, braki danych. Liczby wyłącznie z ``DanePTIE``."""
from __future__ import annotations

from pt_ie_dane import KAT_ZRODLA, L, DanePTIE, Opis
from pt_ie_opis_b import _wykl
from pt_is_opis_b import OPS, wstaw_raport

from lamela.obliczenia.elektryka.bilans import U0

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


GRUPY = {"oswietlenie": "oświetlenie", "gniazda": "gniazda ogólne", "gniazda_kuchnia": "gniazda kuchenne",
         "gniazda_lazienka": "gniazda w łazienkach", "zewn": "gniazda zewnętrzne", "gotowanie": "gotowanie",
         "agd": "AGD (zmywarka, pralka, suszarka)", "pc": "pompa ciepła", "grzalka": "grzałka rezerwowa",
         "sterowanie": "sterowanie ogrzewania", "went": "wentylacja mechaniczna", "ev": "ładowanie EV",
         "napedy": "napędy (bramy, osłony)", "tele": "teletechnika", "pompa": "pompa wody deszczowej"}


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
    Połączenia wyrównawcze — rozdz. „Instalacja piorunochronna, uziom i połączenia wyrównawcze”.

    **Selektywność** (WT § 183 ust. 1 pkt 5): przeciążeniowa zapewniona (I_n zabezpieczenia przedlicznikowego / I_n
    obwodu ≥ 1,6); zwarciowa — częściowa, do granicy wynikającej z tabel producenta aparatów (zestawienie w obliczeniach
    obwodów); aparat główny RG — rozłącznik (nie wyzwala przy zwarciu).

    **Ochrona przed przepięciami** (WT § 183 ust. 1 pkt 10 — obowiązkowa; PN-HD 60364-4-443:2016-03 p. 443.5):
    obliczeniowy poziom ryzyka CRL = f_env/(L_P·N_g) = {L(spd['CRL'], 0)} < {L(_e(D, 'CRL_prog'), 0)}
    (f_env = {L(spd['f_env'], 0)}, L_P = {L(spd['L_P'], 2)} km, N_g = {L(spd['Ng'], 1)}) — ochrona wymagana także
    z warunku normy. W RG: {spd['RG']}. Dalej: {spd['DC']}; {spd['tele']}; {spd['T3']}.
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
        g = grp.setdefault(x.grupa, {"Grupa odbiorników": GRUPY.get(x.grupa, x.grupa), "Obwody": [], "P_i [kW]": 0.0, "k_j": x.k_j,
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
             formaty={"P_el [kW]": 3}, suma=["P_el [kW]"],
             uwagi="Centrala wentylacyjna: moc wentylatorów P = SFP·V przy strumieniu projektowym — ta sama wartość "
                   "co w doborze centrali w PT-3 IS.",
             zrodlo="dobór urządzeń — PT-3 IS; bilans — PT-4")
    P_st = sum(x.P_s for x in b.odbiorniki if x.sterowany)
    P_nst = sum(x.P_s for x in b.odbiorniki if not x.sterowany)
    _w0 = ("; przy obliczeniowej mocy szczytowej odbiorników niesterowanych DLM wstrzymuje ładowanie EV i grzałkę "
           "rezerwową (w = 0) — ładowanie odbywa się poza szczytem poboru" if b.wsp_dlm <= 1e-6 else "")
    o.tekst(f"""
    **Moc szczytowa bez zarządzania mocą** P_s = {L(b.P_s_bez, 1)} kW > moc przyłączeniowa {L(b.P_przyl, 0)} kW —
    **wymagane dynamiczne zarządzanie mocą (DLM)**: ograniczenie prądu ładowania EV i blokada grzałki rezerwowej
    przy przekroczeniu mocy (pomiar prądów faz za licznikiem, sterownik DLM w RG). **Nastawa DLM** z zapasem
    regulacji z = {L(100 * b.par.zapas_DLM, 0)} % [ZAŁ] (czas reakcji, histereza): moc P_lim = {L(b.P_lim, 2)} kW,
    prąd fazowy I_nast = {L(b.I_nast, 1)} A (przy zabezpieczeniu {L(b.I_zab, 0)} A). **Moc szczytowa z DLM**
    P_s,DLM = P_nst + w·P_st = {L(P_nst, 2)} + {L(b.wsp_dlm, 3)}·{L(P_st, 2)} = {L(b.P_s_dlm, 2)} kW ≤
    {L(b.P_przyl, 0)} kW, gdzie w — współczynnik ograniczenia odbiorników sterowanych, ten sam w mocy całkowitej
    i w podziale na fazy (tabela niżej){_w0}; prąd szczytowy I_B = {L(b.I_B, 1)} A ≤ {L(b.I_zab, 0)} A
    (zabezpieczenie przedlicznikowe). Kontrolnie wg N SEP-E-002 (30 kVA + ogrzewanie elektryczne):
    {L(b.sep, 1)} kW [NZW]. Moc przyłączeniowa {L(b.P_przyl, 0)} kW ≤ {L(_e(D, 'grupa_przylaczeniowa_V_moc_max'), 0)} kW
    (grupa V) — do wniosku o warunki przyłączenia.
    """)
    o.tabela([{"Faza": k, "P_s [kW]": v, "I [A]": v * 1000 / (U0 * b.par.cosphi_sr)} for k, v in b.fazy.items()],
             tytul="Podział mocy szczytowej (z DLM) na fazy", formaty={"P_s [kW]": 2, "I [A]": 1},
             uwagi=f"Moc faz z DLM (ten sam współczynnik w = {L(b.wsp_dlm, 3)}); suma faz = P_s,DLM = "
                   f"{L(sum(b.fazy.values()), 2)} kW. Prąd najbardziej obciążonej fazy "
                   f"{L(max(b.fazy.values()) * 1000 / (U0 * b.par.cosphi_sr), 1)} A ≤ nastawa DLM {L(b.I_nast, 1)} A "
                   f"< {L(b.I_zab, 0)} A. Asymetria (max − min)/średnia = {L(100 * b.asymetria, 1)} %; "
                   f"cos φ = {L(b.par.cosphi_sr, 2)}.")


def rozdz_obliczenia(o: Opis, D: DanePTIE):
    """11. Obliczenia — zestawienie wyników i pełne obliczenia bibliotek."""
    ob = D.obw.obwody
    du = max(ob, key=lambda x: x.dU_calk)
    kr = min(ob, key=lambda x: x.I_k1 / x.I_a)
    zaw = min(ob, key=lambda x: x.I_z - x.I_n)
    wybor = [
        ("bilans", "Moc szczytowa z DLM", None), ("bilans", "Prąd szczytowy", None),
        ("bilans", "Najbardziej obciążona faza", None), ("bilans", "Moc przyłączeniowa ≤ 40 kW", None),
        ("obwody", "WLZ: I_n", None), ("obwody", "WLZ: obciążalność", None), ("obwody", "WLZ: spadek", None),
        ("obwody", f"{zaw.odb.id}: I_B ≤ I_n ≤ I_z", f"{zaw.odb.id}: I_B ≤ I_n ≤ I_z (najmniejszy zapas I_z − I_n)"),
        ("obwody", f"{du.odb.id}: ∆U", f"{du.odb.id}: ∆U ZKP → odbiornik (największy spadek)"),
        ("obwody", f"{kr.odb.id}: samoczynne", f"{kr.odb.id}: samoczynne wyłączenie (najmniejszy zapas I_k1/I_a)"),
        ("obwody", "Prąd zwarciowy w RG", None), ("obwody", "SPD wymagany", None), ("obwody", "U_p SPD", None),
        ("obwody", "PWP", None), ("pv", "Moc zainstalowana PV", None), ("pv", "Moc falownika", None),
        ("pv", "U_oc,max", None), ("pv", "Spadek napięcia po stronie DC", None),
        ("odgromowa", "klasa „zwykłe”", None), ("odgromowa", "klasa „wysokie”", None)]
    wiersze = []
    for mod, frag, par in wybor:
        x = _w(D, mod, frag)
        if x is None:
            continue
        w = wiersz(x, par, miejsca=0 if "CRL" in x.opis else 2)
        if mod == "odgromowa" and x.op != "info":                 # ryzyko — zapis wykładniczy
            w.update(wartosc=f"{_wykl(x.wartosc)} {x.jedn}", jedn="", wymaganie=f"≤ {_wykl(x.limit)} {x.jedn}")
        wiersze.append(w)
    n_all = sum(len(D.warunki(k)) for k in ("bilans", "obwody", "pv", "odgromowa"))
    o.rozdzial("Obliczenia", podstawa="§ 23 pkt 8 RPB — założenia, wyniki, dobór", nowa_strona=True)
    o.tekst(f"""
    Obliczenia wykonano bibliotekami `lamela.obliczenia.elektryka` na bieżącym modelu (łącznie {n_all} warunków
    sprawdzających). Zestawienie wyników rozstrzygających — tabela poniżej; w obwodach odbiorczych pokazano obwód
    z najmniejszym zapasem dla każdego kryterium. Pełne obliczenia z wzorami, danymi i wszystkimi warunkami — kolejne podrozdziały.
    """)
    o.dok.tabela_wynikow(wiersze, tytul="Zestawienie wyników sprawdzeń rozstrzygających",
                         uwagi="Warunek niespełniony — rozwiązanie w rozdz. 1 (tabela rozwiązań) i w sprawach otwartych.")
    o.md.append("*[Tabela wyników sprawdzeń rozstrzygających — w PDF]*")
    for k, tyt, pod in (("bilans", "Obliczenia: bilans mocy", "§ 23 pkt 11 lit. a RPB"),
                        ("obwody", "Obliczenia: WLZ, obwody, zabezpieczenia, spadki napięć, samoczynne wyłączenie, SPD, PWP",
                         "PN-HD 60364-4-41, -4-43, -4-443, -5-52"),
                        ("pv", "Obliczenia: instalacja fotowoltaiczna", "PN-HD 60364-7-712"),
                        ("odgromowa", "Obliczenia: ocena ryzyka piorunowego, uziom", "PN-EN 62305-2:2008 (zał. 1 WT)")):
        wstaw_raport(o, D.W[k].raport_md(), tytul=tyt, podstawa=pod, katalog=KAT_ZRODLA,
                     zrodlo=f"lamela.obliczenia.elektryka.{k}")


def rozdz_ppoz(o: Opis, D: DanePTIE):
    """12. Dane dotyczące warunków ochrony przeciwpożarowej (§ 23 pkt 10) — PWP (WT § 183 ust. 2–4)."""
    prog = _e(D, "PWP_kubatura_strefy_prog", 1000)
    V = D.kubatura
    pv = D.pv
    skl = ", ".join(f"{k.replace('plyta', 'płyta')} {L(v, 2)}" for k, v in D.kubatura_skl.items())
    o.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej",
               podstawa="§ 23 pkt 10 RPB; WT § 183 ust. 2–4; ROPoż § 4 ust. 2 pkt 2, § 28a", nowa_strona=True)
    o.tekst(f"""
    **Klasyfikacja** (PAB): budynek mieszkalny jednorodzinny, kategoria zagrożenia ludzi ZL IV, grupa wysokości N;
    jedną strefę pożarową tworzy cały budynek z garażem (WT § 226 ust. 1; W-212).

    **Przeciwpożarowy wyłącznik prądu — sprawdzenie warunku WT § 183 ust. 2.** Przepis wymaga PWP „w strefach
    pożarowych o kubaturze przekraczającej 1000 m³ lub zawierających strefy zagrożone wybuchem” (brzmienie z t.j.
    Dz.U. 2022 poz. 1225). Kubatura strefy = kubatura brutto budynku z modelu (PN-ISO 9836; W-069):
    V = {L(V, 2)} m³ ({skl}); próg {L(prog, 0)} m³ → warunek **{'spełniony — PWP wymagany' if V > prog else 'niespełniony — PWP nie jest wymagany przez WT'}**;
    stref zagrożonych wybuchem brak. ROPoż § 4 ust. 2 pkt 2 wyłącza z obowiązku wyposażania obiektów w PWP
    właścicieli budynków mieszkalnych jednorodzinnych — rozbieżność interpretacyjna (D-04). **Decyzja: PWP
    projektuje się** (spełnia obie interpretacje, W-190).

    **Rozwiązanie PWP:** przycisk w obudowie z szybką, przy wejściu głównym do budynku lub przy ZKP, oznakowany znakiem
    „Przeciwpożarowy wyłącznik prądu” (WT § 183 ust. 3); działa na wyzwalacz aparatu głównego RG (rozłącznik
    z wyzwalaczem wzrostowym z kontrolą ciągłości obwodu albo wyzwalaczem zanikowym [ZAŁ]) i odcina wszystkie obwody
    budynku, w tym stronę AC falownika PV — w budynku nie ma instalacji, których funkcjonowanie jest niezbędne podczas
    pożaru. Zadziałanie PWP nie powoduje samoczynnego załączenia innego źródła energii (WT § 183 ust. 4); falownik PV
    wyłącza się po zaniku napięcia sieci (zabezpieczenie przed pracą wyspową). Strona DC PV pozostaje pod napięciem —
    oznakowanie ostrzegawcze przy RG, PWP i falowniku oraz informacja dla służb ratowniczych przy ZKP.

    **Pozostałe dane ppoż. w zakresie tomu:** mikroinstalacja PV {L(pv.P_kWp, 2)} kWp ≤
    {L(_e(D, 'PV_moc_modulow_max'), 1)} kWp — bez obowiązku uzgodnienia z rzeczoznawcą ds. zabezpieczeń
    przeciwpożarowych i zawiadomienia PSP (W-194, W-218); autonomiczne czujki dymu (PN-EN 14604) — co najmniej
    {L(_e(D, 'czujki_dymu_min'), 0)} w lokalu (ROPoż § 28a ust. 1; Dz.U. 2024 poz. 1716), w projekcie w komunikacji
    każdej kondygnacji i w sypialniach [ZAŁ] (W-197); czujka tlenku węgla — nie dotyczy (brak spalania paliw,
    § 28a ust. 3); przejścia instalacji przez ściany zewnętrzne i płytę poniżej terenu gazoszczelne (W-214); osprzęt
    nie montowany bezpośrednio na podłożu palnym bez osłony (ROPoż § 4 ust. 1 pkt 10); rozdzielnice i PWP dostępne
    (ROPoż § 4 ust. 1 pkt 18 lit. f). Instalacje ochrony przeciwpożarowej (§ 23 pkt 7 lit. j) — nie występują.
    """)
