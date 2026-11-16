#!/usr/bin/env python3
"""Write juror prompt files (J1–J5) that reference the dossier and full concept files."""
from pathlib import Path
OUT = Path('/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/panel')
D = '/home/user/aihouse/umwd/docs'
JURORS = {
 'J1': 'Przewodniczący Sądu, sędzia konkursowy SARP (Warszawa): ocenia ogólną jakość architektoniczną, spójność idei, oryginalność bez efekciarstwa, czytelność prezentowanej idei i jakość warsztatu.',
 'J2': 'Sędzia referent, SARP Wrocław: drobiazgowo analizuje funkcję, zgodność z programem M.01 i wyjaśnieniami (pokoje 24 m², 187 pokoi, cały Sejmik na kondygnacji sali obrad, relacje, ewakuacja, dostawy, garaż), zgodność z MPZP i Regulaminem, wykonalność.',
 'J3': 'Architekt Miasta Wrocławia: ocenia wpisanie w tkankę miasta, pierzeje, skalę, relację z Mostem Grunwaldzkim i bulwarem, przestrzeń publiczną (skwer 9/2, ogród), wytyczne konserwatorskie, sylwetę z osi pl. Grunwaldzkiego, jakość parteru.',
 'J4': 'Marszałek Województwa (Zamawiający) wraz z perspektywą Sekretarza Województwa: reprezentacyjność i godność siedziby Sejmiku, wygoda pracy urzędu i radnych, bezpieczeństwo, koszty budowy (limit 150 mln zł netto, nieprzekraczalny) i eksploatacji, trwałość, wizerunek regionu, dostępność dla mieszkańców.',
 'J5': 'Ekspert Sądu ds. zrównoważonego budownictwa, dostępności i kosztów: zero-emisyjność (EPBD 2024/1275, M.12), ślad węglowy w cyklu życia, energia, woda szara i deszczowa, projektowanie uniwersalne (M.13), realność wyceny i kosztów eksploatacji.',
}
for j, persona in JURORS.items():
    p = f"""ROLA: {persona} Jesteś członkiem 9-osobowego Sądu Konkursowego w konkursie SARP (dwuetapowym, realizacyjnym) na koncepcję budynku administracyjnego Urzędu Marszałkowskiego Województwa Dolnośląskiego z siedzibą Sejmiku, Wrocław, róg Mazowieckiej i Wybrzeża J. Słowackiego, przy Moście Grunwaldzkim.
NAJPIERW przeczytaj: {D}/00_brief_projektowy.md (ograniczenia i kryteria). Teczki pięciu ANONIMOWYCH prac: /tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/panel/dossier.md, a pełne opisy w {D}/20_koncepcja/panel/koncepcja_K1.md … koncepcja_K5.md (przeczytaj przynajmniej części dot. Twojej specjalności). Geometria do sprawdzeń: /home/user/aihouse/umwd/model/site.json (granice.obszar_inwestycji, granice.wydzielenie_A_mpzp), § 13 sąsiada: {D}/30_lokalizacja/sasiedzi.md (okno lokalu 6-6A przy (110,5; 29,0), parapet ≈124,0 m n.p.m.), MPZP: {D}/30_lokalizacja/mpzp.md, program: {D}/20_program/program.md, koszty: {D}/50_research/koszty_benchmarki.md, trendy werdyktów: {D}/50_research/trendy_konkursowe.md. Możesz liczyć w Pythonie (python3 -I; shapely w /home/user/aihouse/.venv-render/bin/python).
ZADANIE: Oceń każdą pracę według kryteriów Regulaminu w skali 1–10: a) efektywność i zasadność rozwiązań przestrzenno-funkcjonalnych i programowych; b) trafność wpisania w tkankę miejską; c) atrakcyjność i oryginalność; d) rozwiązania proekologiczne i energooszczędne; e) dostępność i inkluzywność; f) (drugorzędne) realność i optymalizacja ekonomiczna. Bądź surowy i konkretny; wskaż błędy względem MPZP/Regulaminu/programu/WT (sprawdź liczby i geometrię — np. czy kondygnacja Sejmiku faktycznie mieści się w A, czy 187 pokoi 24/32 m² się mieści, czy dachy są w pasmach 18–25 m / 35–45 m, czy nie ma zjazdu z 1KDG, czy § 13 wobec okna Wybrzeże Słowackiego 5 jest spełniony, czy koszt jest realny). Nie wolno korzystać z informacji o rzeczywistych pracach/wynikach tego konkursu.
WYNIK: zapisz plik {D}/20_koncepcja/panel/ocena_{j}.json o strukturze:
{{"juror": "{j}", "oceny": [{{"id": "K1", "a_funkcja": 0, "b_tkanka": 0, "c_atrakcyjnosc": 0, "d_ekologia": 0, "e_dostepnosc": 0, "f_ekonomia": 0, "mocne": "...", "slabe": "...", "bledy_dyskwalifikujace": "..."}}, ...dla K1–K5], "ranking": ["K?", ...od najlepszej], "przeszczepy": ["pomysł z pracy X, który warto wszczepić zwycięzcy", ...], "uzasadnienie": "..."}}
Pisz po polsku. Nie commituj. Odpowiedz krótko: ranking i 2–3 zdania uzasadnienia."""
    (OUT / f'jury_{j}.txt').write_text(p)
print('ok')
