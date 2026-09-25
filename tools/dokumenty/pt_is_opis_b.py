"""PT-3 IS — część opisowa B: obliczenia i dobory (§ 23 pkt 8 lit. a–b RPB), charakterystyka energetyczna
(§ 23 pkt 11 lit. a–d, W-251), dane ppoż. (§ 23 pkt 10), zasadnicze urządzenia (§ 23 pkt 9), próby i odbiory,
dane do uzupełnienia. Liczby wyłącznie z ``DanePTIS`` (model + obliczenia przy uruchomieniu)."""
from __future__ import annotations

import re
from pathlib import Path

from pt_is_dane import KAT_ZRODLA, L, DanePTIS, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"
RE_IMG = re.compile(r"^!\[(?P<cap>[^\]]*)\]\((?P<src>[^)]+)\)\s*$", re.M)
OPS = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "==": "=", "zakres": "w zakresie"}


def wstaw_raport(o: Opis, tekst: str, *, tytul: str, podstawa: str | None = None, katalog: Path | None = None,
                 zrodlo: str = ""):
    """Raport Markdown biblioteki obliczeniowej jako podrozdział (poziom 2): „# …” → tytuł podrozdziału, „## n. …”
    → poziom 3 (numeracja z nagłówków usunięta — numeruje dokument), obrazy → ilustracje numerowane."""
    tekst = re.sub(r"\A\s*#\s+[^\n]*\n", "", tekst)
    tekst = re.sub(r"^(#{2,4})\s+\d+(?:\.\d+)*\.?\s+", r"\1 ", tekst, flags=re.M)
    tekst = re.sub(r"^(#{2,4})\s", lambda m: m.group(1)[1:] + "# ", tekst, flags=re.M)   # ## → # (+przesunięcie 1)
    o.rozdzial(tytul, poziom=2, podstawa=podstawa, nowa_strona=True)
    poz = 0
    for m in RE_IMG.finditer(tekst):
        if tekst[poz:m.start()].strip():
            o.dok.markdown(tekst[poz:m.start()], przesuniecie=2)
        plik = (katalog or KAT_ZRODLA) / m.group("src")
        if plik.exists():
            o.dok.obraz(plik, podpis=m.group("cap"), szerokosc="100%")
        poz = m.end()
    if tekst[poz:].strip():
        o.dok.markdown(tekst[poz:], przesuniecie=2)
    o.md.append(f"*[Pełna treść obliczeń — w PDF; źródło: {zrodlo}]*")


def wk(D: DanePTIS, modul: str, fragment: str, parametr: str | None = None, miejsca: int = 2) -> dict | None:
    """Wiersz tabeli wyników z pierwszego warunku modułu, którego opis zawiera ``fragment``."""
    x = next((w for w in D.warunki(modul) if fragment in w.opis), None)
    if x is None:
        return None
    lim = x.limit
    lim_t = (f"{L(lim[0], miejsca)}–{L(lim[1], miejsca)}" if isinstance(lim, (list, tuple))
             else L(lim, miejsca) if isinstance(lim, (int, float)) else str(lim or ""))
    return dict(parametr=parametr or x.opis, wartosc=x.wartosc, jedn=x.jedn or "", miejsca=miejsca,
                wymaganie=f"{OPS.get(x.op, x.op)} {lim_t} {x.jedn or ''}".strip() if x.op != "info" else "—",
                podstawa=f"{x.podstawa} [{x.id}]" if x.id else x.podstawa, spelnia=x.ok)


def rozdz_obliczenia(o: Opis, D: DanePTIS):
    """5. Założenia, obliczenia i dobór urządzeń (§ 23 pkt 8 lit. a–b) — zestawienie + pełne obliczenia."""
    obc, w, og, pc = D.obc, D.went, D.og, D.og.pc
    temps = sorted({round(p.theta, 1) for p in obc.pomieszczenia})
    o.rozdzial("Założenia, obliczenia i dobór urządzeń", podstawa="§ 23 pkt 8 lit. a–b RPB", nowa_strona=True)
    o.rozdzial("Parametry klimatu zewnętrznego i wewnętrznego", poziom=2, podstawa="§ 23 pkt 8 lit. a RPB; W-150, W-161")
    o.tekst(f"""
    Klimat zewnętrzny: θ_e = {L(obc.theta_e, 0)} °C (strefa II, W-150), θ_m,e = {L(obc.theta_me, 1)} °C; dane
    godzinowe TMY Poznań (WMO 12330) do bilansu pompy ciepła i charakterystyki energetycznej. Klimat wewnętrzny
    (WT § 134 ust. 2): temperatury obliczeniowe pomieszczeń {', '.join(L(t, 0) for t in temps)} °C (pokoje,
    kuchnia, komunikacja 20 °C; łazienki 24 °C; wartości z modelu). Powietrze zewnętrzne ≥ 20 m³/h na osobę
    ({w.osoby} os.), wywiew wg PN-83/B-03430/Az3 (W-161, W-162). Szczelność budynku n50 = {L(obc.n50, 1)} h⁻¹ [ZAŁ]
    (cel projektowy — potwierdzić próbą ciśnieniową, W-249); sprawność odzysku ciepła η_v = {L(obc.eta_v, 2)}.
    """)
    P7 = dict(zip(pc["T"], pc["P"])).get(-7)
    Wd = D.Wd
    rows = [dict(parametr="Projektowe obciążenie cieplne budynku Φ_HL", wartosc=obc.Phi_HL / 1000, jedn="kW",
                 wymaganie="—", podstawa="PN-EN 12831 [W-151]", spelnia=None),
            dict(parametr=f"Pompa ciepła {pc.get('model')}: moc P(A−7/W35)", wartosc=P7, jedn="kW", miejsca=1,
                 wymaganie="—", podstawa=FIKCJA, spelnia=None),
            wk(D, "ogrzewanie", "Pokrycie mocy przy θ_e", "Pokrycie mocy przy θ_e: P_PC + P_grzałki ≥ Φ_HL + Φ_W"),
            wk(D, "ogrzewanie", "Punkt biwalentny", miejsca=1),
            wk(D, "ogrzewanie", "Udział grzałki", miejsca=4),
            wk(D, "ogrzewanie", "Sezonowa efektywność"),
            wk(D, "ogrzewanie", "Moc nominalna PC", "Moc nominalna PC (R290 — rozp. (UE) 2024/573)", 1),
            wk(D, "ogrzewanie", "Temperatura zasilania ogrzewania podłogowego", miejsca=0),
            dict(parametr="Bufor c.o. / naczynie wzbiorcze c.o.", wartosc=f"{Wd['ogrzewanie']['bufor_l']} / "
                 f"{Wd['ogrzewanie']['naczynie_co_l']}", jedn="dm³", wymaganie="—", podstawa="obliczenia (rozdz. Ogrzewanie)",
                 spelnia=None),
            wk(D, "ogrzewanie", "Poziom mocy akustycznej", miejsca=0),
            wk(D, "ogrzewanie", "Hałas PC w nocy na granicy", miejsca=1),
            wk(D, "ogrzewanie", "Hałas PC w dzień na granicy", miejsca=1),
            wk(D, "ogrzewanie", "Odległość jednostki PC od granicy", miejsca=1),
            wk(D, "ogrzewanie", "Strefa bezpieczeństwa R290", miejsca=0),
            dict(parametr="Wentylacja: nawiew / wywiew", wartosc=f"{L(w.suma_naw, 0)} / {L(w.suma_wyw, 0)}", jedn="m³/h",
                 wymaganie=f"≥ {L(w.naw_min_osoby, 0)} / ≥ {L(w.suma_wyw_min, 0)}", podstawa="WT § 149 [W-161, W-162]",
                 spelnia=w.suma_naw >= w.naw_min_osoby and w.suma_wyw >= w.suma_wyw_min),
            dict(parametr="Centrala: wydajność maks. ≥ strumień okresowy", wartosc=(w.centrala or {}).get("V_max_m3h"),
                 jedn="m³/h", miejsca=0, wymaganie=f"≥ {L(w.V_boost, 0)} m³/h", podstawa="PN-83/B-03430/Az3",
                 spelnia=((w.centrala or {}).get("V_max_m3h") or 0) >= w.V_boost),
            dict(parametr="SFP nawiewu / wywiewu", wartosc=f"{L(w.SFP_naw, 2)} / {L(w.SFP_wyw, 2)}", jedn="kW/(m³/s)",
                 wymaganie=f"≤ {L(w.SFP_lim_naw, 2)} / ≤ {L(w.SFP_lim_wyw, 2)}", podstawa="WT § 154 ust. 10–11 [W-164]",
                 spelnia=w.SFP_naw <= w.SFP_lim_naw and w.SFP_wyw <= w.SFP_lim_wyw),
            wk(D, "woda", "Przepływ obliczeniowy ≤ Q3", miejsca=2),
            wk(D, "woda", "Wymagane ciśnienie w sieci", miejsca=3),
            wk(D, "woda", "Ciśnienie statyczne w punkcie ≤ 0,60 MPa", miejsca=2),
            wk(D, "woda", "Pojemność zasobnika", miejsca=0),
            wk(D, "woda", "Temperatura dezynfekcji", miejsca=0),
            dict(parametr="Kanalizacja: ΣDU / Q_ww", wartosc=f"{L(Wd['kanalizacja']['sum_DU'], 1)} / "
                 f"{L(Wd['kanalizacja']['Q_ww_l_s'], 2)}", jedn="l/s", wymaganie="—", podstawa="PN-EN 12056-2 [W-138]",
                 spelnia=None),
            wk(D, "kanalizacja", "Przykanalik: napełnienie"),
            wk(D, "kanalizacja", "Przykanalik: prędkość"),
            wk(D, "kanalizacja", "Najniższy wpust/przybór powyżej poziomu piętrzenia"),
            dict(parametr="Dachy: A / Q (r = 0,046 l/(s·m²))", wartosc=f"{L(Wd['deszczowa']['A_dachow_m2'], 1)} m² / "
                 f"{L(Wd['deszczowa']['Q_dachy_l_s'], 2)} l/s", jedn="", wymaganie="—",
                 podstawa="PN-EN 12056-3 [W-142]", spelnia=None),
            wk(D, "deszczowa", "Pojemność szczelnego zbiornika", miejsca=1),
            wk(D, "deszczowa", "Niecka: pojemność", miejsca=2),
            wk(D, "deszczowa", "Niecka: czas opróżniania", miejsca=1)]
    o.rozdzial("Zestawienie wyników i dobór urządzeń", poziom=2, podstawa="§ 23 pkt 8 lit. b RPB")
    o.dok.tabela_wynikow([r for r in rows if r], tytul="Podstawowe wyniki obliczeń i sprawdzeń PT-3 IS",
                         uwagi="Pełne sprawdzenia (wszystkie warunki) — w podrozdziałach obliczeń poniżej.",
                         zrodlo="lamela.obliczenia — uruchomienie przy generowaniu tomu")
    o.md.append("**Podstawowe wyniki** (tabela w PDF):\n\n" + "\n".join(
        f"* {r['parametr']}: {r['wartosc'] if isinstance(r['wartosc'], str) else L(r['wartosc'], r.get('miejsca', 2))}"
        f" {r['jedn']} ({r['wymaganie']}; {r['podstawa']})" for r in rows if r))
