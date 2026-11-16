#!/usr/bin/env python3
"""Collect the 5 concept dossiers (K1–K2 from the workflow journal, K3–K5 from JSON files) and build juror prompts."""
import json, sys, re
from pathlib import Path
D = Path('/home/user/aihouse/umwd/docs/20_koncepcja/panel')
J = Path('/root/.claude/projects/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/subagents/workflows/wf_60270687-fbd/journal.jsonl')
OUT = Path('/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/panel')
concepts = {}
for line in J.read_text().splitlines():
    d = json.loads(line)
    if d.get('type') == 'result':
        v = d.get('value') or d.get('result')
        if isinstance(v, dict) and 'nazwa' in v:
            m = re.search(r'koncepcja_(K\d)', v.get('plik', ''))
            k = m.group(1) if m else None
            if k:
                v['id'] = k; concepts[k] = v
for f in sorted(D.glob('koncepcja_K*.json')):
    try:
        v = json.loads(f.read_text())
        k = v.get('id') or re.search(r'(K\d)', f.name).group(1)
        v['id'] = k
        concepts.setdefault(k, v)
    except Exception as e:
        print('ERR', f, e)
for k, v in concepts.items():
    (D / f'koncepcja_{k}.json').write_text(json.dumps(v, ensure_ascii=False, indent=1)) if not (D / f'koncepcja_{k}.json').exists() else None
print('concepts:', sorted(concepts))
def g(v, k):
    return v.get(k) or v.get(k.replace('naslonecznienie', 'nasłonecznienie')) or ''
dossier = '\n\n'.join(
    f"### {k}: {v.get('nazwa')} — „{v.get('haslo')}”\nIdea: {v.get('idea')}\nUrbanistyka: {v.get('urbanistyka')}\nBryły: {json.dumps(v.get('bryly'), ensure_ascii=False)}\n"
    f"Podziemie: {v.get('kondygnacje_podziemne')}\nParter: {v.get('parter')}\nSejmik: {v.get('kondygnacja_sejmiku')}\nBiura: {v.get('kondygnacje_biurowe')}\nElewacje: {v.get('elewacje')}\n"
    f"Zagospodarowanie: {v.get('zagospodarowanie')}\nEkologia: {v.get('ekologia')}\nDostępność: {v.get('dostepnosc')}\nBilans: {json.dumps(v.get('bilans'), ensure_ascii=False)}\n"
    f"Sąsiedzi: {g(v, 'naslonecznienie_sasiedzi')}\nRyzyka (wg autora): {'; '.join(v.get('ryzyka') or [])}\nPełny opis: {v.get('plik') or D / ('koncepcja_' + k + '.md')}"
    for k, v in sorted(concepts.items()))
(OUT / 'dossier.md').write_text(dossier)
print('dossier chars', len(dossier))
