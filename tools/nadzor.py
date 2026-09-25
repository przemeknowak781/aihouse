#!/usr/bin/env python3
"""NADZÓR POSTĘPU (watchdog) — wykrywa zawieszone agenty i brak postępu prac.

Co INTERWAL sekund sprawdza transkrypty aktywnych agentów (Agent-tool i przepływów Workflow) oraz zmiany w repozytorium.
Kryteria zastoju aktywnego agenta:
  * brak jakiegokolwiek zapisu w transkrypcie ≥ BEZCZYNNOSC_MIN minut,
  * brak wywołania narzędzia ≥ BEZ_NARZEDZI_MIN minut,
  * ≥ 2 komunikaty „Output token limit hit” w ciągu ostatnich 60 minut (pętla zbyt długich odpowiedzi).
Stan zapisuje w raporty/nadzor.json (do kolaży); przy NOWYM zastoju dopisuje raporty/nadzor.log i KOŃCZY działanie
(zakończenie procesu w tle budzi orkiestratora, który diagnozuje i restartuje agenta, po czym uruchamia nadzór ponownie).
Użycie: python3 tools/nadzor.py [--raz]   (--raz: jednorazowy raport stanu na stdout, bez pętli)
"""
import json
import sys
import time
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SES = Path("/root/.claude/projects/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/subagents")
IGNORUJ = ROOT / "raporty" / "nadzor_ignoruj.txt"     # id agentów / katalogów wf zatrzymanych celowo
STAN = ROOT / "raporty" / "nadzor.json"
LOG = ROOT / "raporty" / "nadzor.log"
INTERWAL = 180
BEZCZYNNOSC_MIN = 20
BEZ_NARZEDZI_MIN = 30
TZ = ZoneInfo("Europe/Warsaw")


def ts(s):
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def ignorowane():
    if not IGNORUJ.exists():
        return set()
    return {l.split("#")[0].strip() for l in IGNORUJ.read_text().splitlines() if l.split("#")[0].strip()}


def analiza_transkryptu(p: Path):
    """Zwraca (czy_zakonczony, t_ost_narzedzia, limity_60min, t_ost_zapisu)."""
    size = p.stat().st_size
    with open(p, "rb") as f:
        f.seek(max(0, size - 600_000))
        tail = f.read().decode("utf-8", "ignore").splitlines()[1:]
    t_tool, limity, ost = None, [], None
    for l in tail:
        try:
            d = json.loads(l)
        except Exception:
            continue
        t = ts(d.get("timestamp", "")) or t
        m = d.get("message") or {}
        c = m.get("content")
        if isinstance(c, str) and "Output token limit" in c:
            limity.append(t)
        if isinstance(c, list):
            for b in c:
                if b.get("type") == "tool_use":
                    t_tool = t
        if d.get("type") in ("assistant", "user"):
            ost = d
    zakonczony = False
    if ost is not None and ost.get("type") == "assistant":
        c = (ost.get("message") or {}).get("content")
        if isinstance(c, list) and c and all(b.get("type") in ("text", "thinking") for b in c):
            zakonczony = True
    teraz = time.time()
    lim60 = [x for x in limity if x and teraz - x < 3600]
    return zakonczony, t_tool, len(lim60), p.stat().st_mtime


def agenci():
    ign = ignorowane()
    wyn = []
    # agenci uruchomieni narzędziem Agent
    for meta in SES.glob("agent-*.meta.json"):
        aid = meta.name[len("agent-"):-len(".meta.json")]
        if aid in ign:
            continue
        j = SES / f"agent-{aid}.jsonl"
        if not j.exists():
            continue
        opis = json.loads(meta.read_text()).get("description", aid)
        zak, t_tool, lim, mt = analiza_transkryptu(j)
        # zakończenie agenta Agent-tool potwierdza orkiestrator wpisem do nadzor_ignoruj.txt; heurystyka pomocnicza:
        # ostatni wpis to tekst asystenta i brak zapisu > 3 min
        # heurystyka „ostatni wpis = tekst” jest zawodna (agent dzieli pracę tekstem i długo generuje kolejny plik) —
        # agent jest zakończony WYŁĄCZNIE po wpisie orkiestratora do nadzor_ignoruj.txt (po powiadomieniu o zakończeniu)
        wyn.append(dict(id=aid, opis=opis, zrodlo="agent", aktywny=True, t_tool=t_tool, limity=lim, mtime=mt))
    # agenci przepływów Workflow
    for wf in SES.glob("workflows/wf_*"):
        if wf.name in ign:
            continue
        jr = wf / "journal.jsonl"
        if not jr.exists():
            continue
        started, done = {}, set()
        for l in jr.read_text().splitlines():
            try:
                d = json.loads(l)
            except Exception:
                continue
            if d.get("type") == "started":
                started[d["agentId"]] = d.get("label", d["agentId"])
            elif d.get("type") == "result":
                done.add(d.get("agentId"))
        for aid, label in started.items():
            if aid in ign or aid in done:
                continue
            j = wf / f"agent-{aid}.jsonl"
            if not j.exists():
                continue
            zak, t_tool, lim, mt = analiza_transkryptu(j)
            # dla agentów przepływów rozstrzyga dziennik (brak wpisu "result" = agent pracuje), nie ostatni wpis transkryptu
            wyn.append(dict(id=aid, opis=f"{wf.name}:{label}", zrodlo="workflow", aktywny=True, t_tool=t_tool, limity=lim, mtime=mt))
    return wyn


def ostatnia_zmiana_repo():
    naj = 0
    for p in list(ROOT.glob("docs/**/*")) + list(ROOT.glob("projekt/**/*")) + list(ROOT.glob("model/**/*")) + list(ROOT.glob("src/**/*.py")):
        if p.is_file():
            naj = max(naj, p.stat().st_mtime)
    return naj


def ocena():
    teraz = time.time()
    lista = agenci()
    zastoje = []
    for a in lista:
        if not a["aktywny"]:
            continue
        idle = (teraz - a["mtime"]) / 60
        bez_nar = (teraz - a["t_tool"]) / 60 if a["t_tool"] else None
        powody = []
        if idle >= BEZCZYNNOSC_MIN:
            powody.append(f"brak zapisu {idle:.0f} min")
        if bez_nar is not None and bez_nar >= BEZ_NARZEDZI_MIN:
            powody.append(f"brak wywołań narzędzi {bez_nar:.0f} min")
        if a["limity"] >= 2:
            powody.append(f"{a['limity']}× limit długości odpowiedzi w 60 min")
        a["idle_min"] = round(idle, 1)
        a["bez_narzedzi_min"] = round(bez_nar, 1) if bez_nar is not None else None
        a["powody"] = powody
        if powody:
            zastoje.append(a)
    repo_min = (teraz - ostatnia_zmiana_repo()) / 60
    stan = dict(czas=datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
                aktywni=[{k: a.get(k) for k in ("id", "opis", "idle_min", "bez_narzedzi_min", "limity", "powody")} for a in lista if a["aktywny"]],
                zakonczeni=len([a for a in lista if not a["aktywny"]]),
                zastoje=[{k: a.get(k) for k in ("id", "opis", "powody")} for a in zastoje],
                repo_bez_zmian_min=round(repo_min, 1))
    STAN.write_text(json.dumps(stan, ensure_ascii=False, indent=1), encoding="utf-8")
    return stan


def main():
    if "--raz" in sys.argv:
        print(json.dumps(ocena(), ensure_ascii=False, indent=1))
        return
    zgloszone = set()
    while True:
        stan = ocena()
        nowe = [z for z in stan["zastoje"] if z["id"] not in zgloszone]
        if nowe:
            with open(LOG, "a", encoding="utf-8") as f:
                for z in nowe:
                    f.write(f"{stan['czas']}  ZASTÓJ  {z['opis']} ({z['id']}): {'; '.join(z['powody'])}\n")
            print("NADZÓR: WYKRYTO ZASTÓJ →", json.dumps(nowe, ensure_ascii=False))
            return
        if stan["aktywni"] and stan["repo_bez_zmian_min"] >= 45 and "repo" not in zgloszone:
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(f"{stan['czas']}  OSTRZEŻENIE  brak zmian w repozytorium od {stan['repo_bez_zmian_min']} min\n")
            print("NADZÓR: brak postępu w repozytorium od", stan["repo_bez_zmian_min"], "min")
            return
        time.sleep(INTERWAL)


if __name__ == "__main__":
    main()
