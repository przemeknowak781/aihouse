"""Raport kompletności tomu I w Markdown (walidator ``sprawdz_tom`` + kontrole pliku ``tom_I_kontrole``)."""
from __future__ import annotations

import time

ZNAK = {"OK": "✓", "BRAK": "✗", "DO UZUPEŁNIENIA": "…", "N/D": "–", "OSTRZEŻENIE": "!"}
POMIN = ("[ZAŁ]", "[NZW]", "[INT]", "[PROG]")


def _k(t) -> str:
    return str(t).replace("|", "\\|").replace("\n", " ")


def _podsumowanie_uzup(r, kontrole: list) -> str:
    """Rozbicie statusu DO UZUPEŁNIENIA: dane osobowe na stronach tytułowych a treść zastępcza (dane przykładowe,
    strony zastępcze dokumentów, analizy bez danych wejściowych, metryki rysunków) — rejestr E.1."""
    du = [p for p in r.pozycje if p.status == "DO UZUPEŁNIENIA"]
    osob = [p.id for p in du if "stronie tytułowej" in (p.szczegoly or "")]
    zast = [f"{p.id} ({p.szczegoly.split(';')[-1].strip()})" for p in du if p.id not in osob]
    zast += [f"{k['id']} ({k['szczegoly']})" for k in kontrole if k["status"] == "DO UZUPEŁNIENIA"]
    return (f"Pozycje „DO UZUPEŁNIENIA”: {len(du)} — dane osobowe i identyfikatory na stronach tytułowych "
            f"({len(osob)}: {', '.join(osob) or '—'}); treść zastępcza, której nie wolno traktować jako kompletnej "
            f"({len(zast)}): " + ("; ".join(zast) if zast else "—") + ".")


def raport_md(r, w, kontrole: list, wekt: list, zrodla: dict, otwarte: dict) -> str:
    s = r.podsumowanie()
    L = [f"# Raport kompletności — {r.plik}", "",
         f"*Wygenerowano {time.strftime('%Y-%m-%d %H:%M')} przez `tools/dokumenty/zloz_tom_I.py` "
         f"(walidator `lamela.dokumenty.sprawdz_tom`, lista „{r.lista}”). Walidator ocenia obecność treści "
         "wymaganej przepisami (wyrażenia regularne), nie jej poprawność merytoryczną.*", "",
         f"**Status tomu: {r.status}**", "",
         f"| OK | BRAK | DO UZUPEŁNIENIA | N/D | OSTRZEŻENIE | znaczniki [DO UZUPEŁNIENIA] | [DOKUMENT ZEWNĘTRZNY] "
         f"| [DANE PRZYKŁADOWE] |", "|---:|---:|---:|---:|---:|---:|---:|---:|",
         f"| {s['OK']} | {s['BRAK']} | {s['DO UZUPEŁNIENIA']} | {s['N/D']} | {s['OSTRZEŻENIE']} | "
         f"{s['znaczniki_do_uzupelnienia']} | {s['znaczniki_dokument_zewnetrzny']} | "
         f"{s['znaczniki_dane_przykladowe']} |", "",
         _podsumowanie_uzup(r, kontrole), "",
         f"Plik: `projekt/wydanie/{w.nazwa}` — {w.strony} stron, {w.rozmiar_mb:.2f} MB; nazwa wg zał. 1 RPB: "
         f"{'zgodna' if w.nazwa_zgodna else 'NIEZGODNA'}.", "",
         "## 1. Skład tomu (RPB § 5 ust. 1, 3–4; § 7 ust. 7 pkt 1)", "",
         "| element | tytuł | strony pliku | strony A4 (numeracja „strona X z Y”) | arkusze |",
         "|---|---|---|---:|---:|"]
    for e in w.elementy:
        do = e["start"] + e["strony"] - 1
        L.append(f"| {e['kod']} | {_k(e['tytul'])} | {e['start']}–{do} | {e['strony_opisu'] or e['strony']} "
                 f"| {e['arkusze']} |")
    n_fr = (w.elementy[0]["start"] - 1) if w.elementy else 0
    L += ["", f"Strony 1–{n_fr} pliku: strona tytułowa tomu i łączny spis treści ze spisem załączników "
              f"(numeracja „TOM I · strona X z {n_fr}”).", "",
          "Źródła rysunków: PZT — `" + zrodla["PZT"] + "`; PAB — `" + zrodla["PAB"] + "`.", "",
          f"> PAB: {zrodla['PAB_info']}.", "",
          "## 2. Lista kontrolna TOM_I (rejestr wymagań, sekcja C.1)", "",
          "| | id | el. | status | wymaganie | podstawa | szczegóły |", "|---|---|---|---|---|---|---|"]
    for p in r.pozycje:
        L.append(f"| {ZNAK.get(p.status, '?')} | {p.id} | {p.element} | {p.status} | {_k(p.opis)} | {_k(p.podstawa)} "
                 f"| {_k(p.szczegoly)} |")
    L += ["", "## 3. Kontrole pliku (RPB § 2b; W-300)", "",
          "| | id | kontrola | status | podstawa | szczegóły |", "|---|---|---|---|---|---|"]
    for k in kontrole:
        L.append(f"| {ZNAK.get(k['status'], '?')} | {k['id']} | {_k(k['opis'])} | {k['status']} | {_k(k['podstawa'])} "
                 f"| {_k(k['szczegoly'])} |")
    L += ["", "### 3.1. Arkusze rysunkowe w tomie", "",
          "| nr | strona pliku | format | wymiary [mm] | skala | ścieżki wektorowe | znaki tekstu | raster [%] | status |",
          "|---|---:|---|---|---|---:|---:|---:|---|"]
    for a in wekt:
        L.append(f"| {a['nr']} | {a['strona']} | {a['format']} | {a['wymiary_mm'][0]} × {a['wymiary_mm'][1]} | "
                 f"{a['skala']} | {a['sciezki']} | {a['znaki']} | {a['udzial_rastra'] * 100:.1f} | "
                 f"{'arkusz zastępczy' if a['zastepczy'] else a['status']} |")
    lista = (r.znaczniki or {}).get("lista") or {}
    L += ["", "## 4. Pola do uzupełnienia i dokumenty zewnętrzne (wystąpienia w pliku)", "",
          "Dane osobowe, numery uprawnień, podpisy i dokumenty organów uzupełnia projektant/Inwestor — system ich "
          "nie tworzy. Status „PRZYKŁAD – NIE DO ZŁOŻENIA” utrzymuje się do usunięcia wszystkich pól.", "",
          "| wystąpienia | pole |", "|---:|---|"]
    for t, n in sorted(lista.items(), key=lambda x: (-x[1], x[0])):
        if "DANE PRZYKŁADOWE" in t or t in POMIN:
            continue
        L.append(f"| {n} | {_k(t)} |")
    L += ["", "## 5. Sprawy otwarte (z generatorów)", ""]
    for grupa, poz in otwarte.items():
        if poz:
            L.append(f"**{grupa.replace('_', ' ')}**")
            L.append("")
            L += [f"- {_k(x)}" for x in poz]
            L.append("")
    return "\n".join(L) + "\n"
