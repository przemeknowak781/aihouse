#!/usr/bin/env python3
"""Arkusze kontaktowe konkursu wewnętrznego: (1) koncepcje K1–K5, (2) wyniki panelu sędziowskiego J1–J5.
Źródła: docs/20_koncepcja/panel/koncepcja_K*.json, ocena_J*.json, werdykt_panelu.md (bez jakichkolwiek danych o rzeczywistym konkursie)."""
import json, html, subprocess, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; P = ROOT/'docs/20_koncepcja/panel'; OUT = ROOT/'prezentacja/kontakt'
OUT.mkdir(parents=True, exist_ok=True)
K = {f'K{i}': json.loads((P/f'koncepcja_K{i}.json').read_text()) for i in range(1, 6)}
J = {f'J{i}': json.loads((P/f'ocena_J{i}.json').read_text()) for i in range(1, 6)}
CR = [('a_funkcja','a funkcja'),('b_tkanka','b tkanka'),('c_atrakcyjnosc','c atrakcyjność'),('d_ekologia','d ekologia'),('e_dostepnosc','e dostępność'),('f_ekonomia','f ekonomia')]
def score(o): return sum(o[k] for k,_ in CR[:5]) + 0.5*o['f_ekonomia']
sc = {k: {j: score(next(o for o in J[j]['oceny'] if o['id']==k)) for j in J} for k in K}
avg = {k: sum(v.values())/5 for k,v in sc.items()}
borda = {k: sum(4-J[j]['ranking'].index(k) for j in J) for k in K}
order = ['K5','K4','K1','K3','K2']   # werdykt panelu (remisy rozstrzygnięte w werdykt_panelu.md)
place = {k:i+1 for i,k in enumerate(order)}
crit = {k: {c: sum(next(o for o in J[j]['oceny'] if o['id']==k)[c] for j in J)/5 for c,_ in CR} for k in K}
e = html.escape
def f1(x): return f'{x:.1f}'.replace('.',',')
def num(x): return f'{x:,.0f}'.replace(',', ' ')
CSS = """<style>@page{margin:0} body{margin:0;font-family:'Inter','DejaVu Sans',sans-serif;color:#1d1b18;background:#fff}
.wrap{padding:22mm 20mm} h1{font-size:30pt;font-weight:600;margin:0} .sub{font-size:13pt;color:#6b655c;margin:2mm 0 10mm}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:7mm} .card{border:0.4mm solid #d9d3c9;border-radius:2mm;padding:6mm;display:flex;flex-direction:column}
.card.win{border:0.8mm solid #a8332a} .id{font-size:30pt;font-weight:700;color:#a8332a;line-height:1} .pl{float:right;font-size:11pt;background:#1d1b18;color:#fff;padding:1mm 3mm;border-radius:1mm}
.nm{font-size:12.5pt;font-weight:600;margin:3mm 0 2mm;min-height:22mm} .mt{font-size:10.5pt;font-style:italic;color:#57524b;margin-bottom:3mm;min-height:26mm}
.idea{font-size:9.5pt;line-height:1.35;color:#333;min-height:62mm} table.kv{width:100%;font-size:9.5pt;border-collapse:collapse;margin-top:3mm} table.kv td{padding:0.8mm 0;border-bottom:0.2mm solid #eee} table.kv td:last-child{text-align:right;font-weight:600}
.hd{font-size:10pt;font-weight:600;margin:4mm 0 1mm;color:#6b655c;text-transform:uppercase;letter-spacing:0.3pt}
.res{font-size:10pt;margin-top:3mm;padding-top:2mm;border-top:0.3mm solid #d9d3c9}
table.t{border-collapse:collapse;font-size:12pt;width:100%} table.t th,table.t td{padding:2.2mm 3mm;border-bottom:0.3mm solid #e2ddd4;text-align:right} table.t th:first-child,table.t td:first-child{text-align:left}
table.t th{background:#f3f0ea;font-weight:600} tr.win td{font-weight:700;color:#a8332a} .two{display:grid;grid-template-columns:1.1fr 1fr;gap:10mm;margin-top:8mm}
.q{font-size:10pt;line-height:1.38;margin-bottom:3mm} .q b{color:#a8332a} ul{margin:0;padding-left:5mm;font-size:10pt;line-height:1.35} .note{font-size:9.5pt;color:#6b655c;margin-top:6mm}</style>"""
def bars(k):
    W,H=260,120; s=[f'<svg width="100%" viewBox="0 0 {W} {H+28}" xmlns="http://www.w3.org/2000/svg">']
    ymax=46; y=lambda h: H-h/ymax*H
    s.append(f'<rect x="0" y="{y(45):.1f}" width="{W}" height="{y(35)-y(45):.1f}" fill="#f6e3df"/><text x="{W-2}" y="{y(45)+8:.1f}" font-size="7" text-anchor="end" fill="#a8332a">MPZP A 35–45 m</text>')
    s.append(f'<rect x="0" y="{y(25):.1f}" width="{W}" height="{y(18)-y(25):.1f}" fill="#eef0ea"/><text x="{W-2}" y="{y(25)+8:.1f}" font-size="7" text-anchor="end" fill="#5b6b4c">18–25 m</text>')
    bl=K[k]['bryly']; n=len(bl); bw=(W-10)/n-8
    for i,b in enumerate(bl):
        h=b.get('wysokosc_najwyzszy_pkt_dachu_m') or 0; x=8+i*(bw+8)
        s.append(f'<rect x="{x:.1f}" y="{y(h):.1f}" width="{bw:.1f}" height="{H-y(h):.1f}" fill="#3a3632"/>')
        s.append(f'<text x="{x+bw/2:.1f}" y="{y(h)-2:.1f}" font-size="8" text-anchor="middle" fill="#1d1b18">{f1(h)} m</text>')
        lab=re.split(r'[–—(]',b['nazwa'])[0].strip()[:18]
        s.append(f'<text x="{x+bw/2:.1f}" y="{H+10}" font-size="6.5" text-anchor="middle" fill="#57524b">{e(lab)}</text>')
        s.append(f'<text x="{x+bw/2:.1f}" y="{H+19}" font-size="6.5" text-anchor="middle" fill="#57524b">{b.get("kondygnacje_nadziemne","")} kond.</text>')
    s.append(f'<line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="#1d1b18" stroke-width="0.8"/></svg>'); return ''.join(s)
def short(t,n):
    t=re.sub(r'\s+',' ',t).strip(); return t if len(t)<=n else t[:n].rsplit(' ',1)[0]+' …'
cards=[]
for k in sorted(K):
    d=K[k]; b=d['bilans']
    nm=re.sub(r'^K\d\s*[—–-]\s*','',d['nazwa']).replace('„','').replace('”','').replace('"','').strip()
    cards.append(f"""<div class="card{' win' if k=='K5' else ''}"><div><span class="id">{k}</span><span class="pl">miejsce {place[k]}</span></div>
<div class="nm">{e(short(nm,95))}</div><div class="mt">„{e(short(d['haslo'],150))}”</div><div class="idea">{e(short(d['idea'],560))}</div>
<div class="hd">Bryły – wysokość dachu</div>{bars(k)}
<table class="kv"><tr><td>PC nadziemna</td><td>{num(b['pc_nadziemna_m2'])} m²</td></tr><tr><td>PC podziemna</td><td>{num(b['pc_podziemna_m2'])} m²</td></tr>
<tr><td>PU</td><td>{num(b['pu_m2'])} m²</td></tr><tr><td>Pow. zabudowy</td><td>{num(b['pow_zabudowy_m2'])} m²</td></tr><tr><td>Wysokość max</td><td>{f1(b['wysokosc_max_m'])} m</td></tr>
<tr><td>Koszt (deklaracja)</td><td>{f1(b['koszt_mln_zl_netto'])} mln zł</td></tr></table>
<div class="res">Panel: średnia <b>{f1(avg[k])}</b>/55 · Borda <b>{borda[k]}</b>/20</div></div>""")
h1=f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">{CSS}<style>@page{{size:600mm 340mm}}</style></head><body><div class="wrap">
<h1>Konkurs wewnętrzny – koncepcje K1–K5</h1><div class="sub">Pięć niezależnych koncepcji architektoniczno-urbanistycznych (opisy i dane: docs/20_koncepcja/panel/). Koncepcje powstały jako specyfikacje tekstowe bez rysunków – schemat pokazuje wysokości brył na tle pasm MPZP.</div>
<div class="grid">{''.join(cards)}</div><div class="note">Liczby z deklaracji autorów koncepcji (bilans w koncepcja_K*.json); wynik panelu z ocena_J*.json. Zwycięska K5 została rozwinięta w koncepcję „BRAMA I LATARNIA” z przeszczepami z K1, K3 i K4.</div></div></body></html>"""
rows=''.join(f"<tr class=\"{'win' if k=='K5' else ''}\"><td>{place[k]}. {k}</td>"+''.join(f"<td>{f1(sc[k][j])}</td>" for j in J)+f"<td>{f1(avg[k])}</td><td>{borda[k]}</td><td>{' / '.join(str(J[j]['ranking'].index(k)+1) for j in J)}</td></tr>" for k in order)
crows=''.join(f"<tr class=\"{'win' if k=='K5' else ''}\"><td>{k}</td>"+''.join(f"<td style=\"background:rgba(168,51,42,{(crit[k][c]-4.5)/5:.2f})\">{f1(crit[k][c])}</td>" for c,_ in CR)+"</tr>" for k in order)
roles={'J1':'funkcja i geometria','J2':'funkcja i wykonalność','J3':'Architekt Miasta – tkanka','J4':'Zamawiający – budżet, godność','J5':'zero-emisyjność, LCA, koszt'}
quotes=''.join(f"<div class=\"q\"><b>{j}</b> ({roles[j]}; ranking {' > '.join(J[j]['ranking'])}): {e(short(J[j]['uzasadnienie'],330))}</div>" for j in J)
md=(P/'werdykt_panelu.md').read_text()
weak=[re.sub(r'\*\*','',m.group(1)).strip() for m in re.finditer(r'^\| \d+ \| (.+?) \|', md.split('## 4.')[1].split('## 5.')[0], re.M)][:10]
graft=[(m.group(1).strip(),m.group(2).strip(),m.group(3).strip()) for m in re.finditer(r'^\| (K[\d/()K ]+) \| (.+?) \| [J\d, ]+ \| (.+?) \|$', md.split('## 5.')[1], re.M)]
h2=f"""<!doctype html><html lang="pl"><head><meta charset="utf-8">{CSS}<style>@page{{size:600mm 340mm}}</style></head><body><div class="wrap">
<h1>Konkurs wewnętrzny – wyniki panelu sędziowskiego</h1><div class="sub">Pięciu niezależnych sędziów (J1–J5) oceniło koncepcje K1–K5 wg kryteriów regulaminu (a–e pierwszorzędne, f ekonomia z wagą ½; max 55 pkt) i ułożyło rankingi (Borda: 4–3–2–1–0). Werdykt: <b style="color:#a8332a">K5 – jednogłośnie, 5/5 pierwszych miejsc</b>.</div>
<div class="two"><div><table class="t"><tr><th>Praca</th><th>J1</th><th>J2</th><th>J3</th><th>J4</th><th>J5</th><th>Średnia</th><th>Borda</th><th>Miejsca u sędziów</th></tr>{rows}</table>
<div class="hd" style="margin-top:8mm">Średnie oceny w kryteriach (0–10)</div><table class="t"><tr><th>Praca</th>{''.join(f'<th>{l}</th>' for _,l in CR)}</tr>{crows}</table>
<div class="note">K4 i K1 remisują (39,9; Borda 12) – rozstrzyga porównanie parami 3 : 2 dla K4. K3 i K2 remisują w średniej – rozstrzyga Borda. Żaden sędzia nie stwierdził błędu dyskwalifikującego.</div>
<div class="hd" style="margin-top:8mm">Główne słabości K5 wskazane przez sędziów (usunięte w koncepcji wybranej)</div><ul>{''.join(f'<li>{e(w)}</li>' for w in weak)}</ul></div>
<div><div class="hd">Uzasadnienia sędziów (skrót)</div>{quotes}
<div class="hd" style="margin-top:6mm">Przeszczepy do K5</div><ul>{''.join(f'<li><b>{e(s)}</b>: {e(short(p,110))} – <i>{e(short(dcs,60))}</i></li>' for s,p,dcs in graft[:12])}</ul></div></div></div></body></html>"""
for name,h in (('kontakt_konkurs_wewnetrzny_koncepcje',h1),('kontakt_konkurs_wewnetrzny_wyniki_jury',h2)):
    hp=OUT/f'{name}.html'; hp.write_text(h,encoding='utf-8')
    subprocess.run(['node',str(ROOT/'tools/plansze/html2pdf.js'),str(hp),str(OUT/f'{name}.pdf'),'600','340','--png',str(OUT/f'{name}.png'),'--pngw','6000'],check=True)
    hp.unlink(); print(name)
