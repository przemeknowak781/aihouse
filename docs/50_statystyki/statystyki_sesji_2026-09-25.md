# Statystyki sesji „Dom LAMELA” — agenci, czas, iteracje, koszt porównawczy

Migawka: wątek główny do 08:29Z, podagenci do 08:38Z (10:29–10:38 CEST), 25.09.2026. Praca trwa (etap wydania),
więc wartości końcowe będą wyższe. Dane zebrało 5 agentów, a 2 niezależni weryfikatorzy przeliczyli tokeny od zera
i sprawdzili źródła (pełne raporty i dane: `dane/`).

## Czas i agenci

| Miara | Wartość |
|---|---|
| Czas zegarowy sesji | 23:07Z 24.09 → 08:38Z 25.09 = **9 h 31 min** |
| Wiadomości człowieka | **12** (+ 2 odpowiedzi na pytania wyboru) |
| Agenci pracy projektowej | **80**: 15 samodzielnych + 65 w 10 przepływach (workflow) |
| Agenci tego zestawienia | 7 (przepływ statystyk) |
| Uruchomienia przepływów | 12 wywołań, 11 identyfikatorów (1 wznowienie, 3 zatrzymania) |
| Suma czasu pracy agentów | **2 983 min ≈ 49,7 h** |
| Średnia równoległość / maksimum | 5,2 agenta / **9 naraz** |
| Odpowiedzi API (wszystkie) | 9 121 (wątek główny 746, podagenci 8 375) |
| Wywołania narzędzi | 9 753 (wątek główny 747, podagenci 9 006; w tym Bash 7 364) |
| Kompakcje kontekstu | 2 w wątku głównym + 5 u samodzielnych agentów |

## Iteracje

- Model budynku: 3 fale poprawek (runda 1 z panelu koncepcji, runda 2, domknięcie w wydaniu) + trwająca pętla
  konstrukcyjna (runda 1 z maks. 3).
- Role agentów w przepływach: produkcja 34, weryfikacja/audyt 20, poprawki 11, sędziowie 3.
- 7 przepływów przeszło ≥ 1 rundę weryfikacja → poprawki.
- Panel koncepcji uruchamiany 3 razy (korekta Inwestora „S” zamiast tarasu; zawieszony wariant W3 → wznowienie).
- 17 wiadomości korygujących do 8 agentów; 1 przypadkowa druga egzekucja agenta syntezy (koszt ≈ 23 USD).
- 402 commity (287 autocommitów), 50 plansz postępu (do 10:30 CEST).

## Tokeny i koszt według cennika API

Model: wyłącznie `claude-opus-5-5`. Ceny (USD/MTok) z oficjalnej strony
https://platform.claude.com/docs/en/about-claude/pricing (odczyt 25.09.2026, potwierdzone przez weryfikatora):
input 4; output 20; zapis cache 5 min 5, 1 h 8; odczyt cache 0,20 (0,05× — stawka szczególna dla Opus 5.5).

| Składnik | Tokeny | Koszt USD |
|---|---|---|
| Odczyt z cache | 2 846,1 mln | 569,23 |
| Zapis do cache (5 min / 1 h) | 49,0 mln / 1,7 mln | 258,66 |
| Output (w tym thinking) | 13,65 mln szac. (zapisane 3,87 mln — dolna granica) | 273,08 |
| Input bez cache | 18 464 | 0,07 |
| **Razem** | | **≈ 1 101 USD** (dolna granica 905 USD) |
| Bez cache (hipotetycznie) | | ≈ 11 861 USD |

- Przeliczenie: kurs średni NBP 3,8570 PLN/USD (tabela 186/A/NBP/2026 z 24.09.2026) → **≈ 4 250 zł**
  (dolna granica ≈ 3 490 zł).
- Output podagentów jest częściowo szacowany: 70 % odpowiedzi w transkryptach ma tylko początkowe `usage`; estymator
  skalibrowany na 2 486 pełnych odpowiedziach, walidacja krzyżowa 0,986–1,017.
- To koszt porównawczy według cennika API; faktyczne rozliczenie w planie subskrypcyjnym (Pro/Max) jest inne
  i nie da się go ustalić z danych sesji.

## Porównanie z biurem projektowym (Polska 2024–2026)

Zakres: koncepcja + PZT + PAB + PT (AR, BO, IS z charakterystyką energetyczną, IE z PV) + wizualizacje + strona.
Widełki po korekcie weryfikatora źródeł:

| | Biuro projektowe | Ta sesja |
|---|---|---|
| Koszt | **40–130 tys. zł netto**, najpewniej **60–95 tys.** | ≈ 4,25 tys. zł (cennik API) |
| Czas | **10–32 tygodni** | 9,5 h zegarowo (niezakończone) |
| Pracochłonność | ok. **400–1 100 h** (szacunek) | 49,7 h pracy agentów + 12 wiadomości człowieka |

Źródła główne: rozporządzenie MRiT Dz.U. 2021 poz. 2458 (wskaźniki W%); ZWPP SARP (uchwała nr 70/2014); GUS
„Struktura wynagrodzeń wg zawodów X 2024”; cenniki rynkowe (m.in. BIAMS, Disinn, DraftSanit, muratordom,
Ciemińscy) — pełna tabela 29 źródeł z URL, cytatami i oceną wiarygodności: `dane/raport_koszt_pracy_ludzi.md`,
`dane/raport_weryfikacja_zrodel.md`.

**Dlaczego to nie jest porównanie 1:1:**
1. Biuro dostarcza dokumentację podpisaną przez projektantów z uprawnieniami, z odpowiedzialnością zawodową i OC,
   opartą na realnej mapie, badaniach gruntu, MPZP i warunkach przyłączenia. Tu działka, MPZP i grunt są fikcyjne,
   a pola projektantów — [DO UZUPEŁNIENIA].
2. Dokumentacja nie jest gotowa do złożenia: PT-2 BO ma 42 pozycje niezamknięte, trwa pętla konstrukcyjna i wydanie.
3. Koszt sesji rośnie do końca prac; koszt biura nie obejmuje mapy, geotechniki, opłat ani nadzoru autorskiego.
4. Widełki dla biura opierają się w dużej części na cennikach rynkowych o ograniczonej wiarygodności.

## Produkt (repozytorium na HEAD d4716b00)

- 65 arkuszy PDF w repozytorium (+ 5 arkuszy PT-AR wygenerowanych później); 5 tomów, 609 stron.
- Python: 84 084 linii (src 64 746, tools 19 338), 158 funkcji testowych.
- Rejestr wymagań: 418 pozycji; 132 pozycje obliczeń statycznych; 22 węzły mostków 2D.
- Model: 57 ścian, 50 otworów, 33 pomieszczenia, 20 płyt, 38 belek.
- Markdown: 536 tys. słów (bez wyników testowych).

Uwaga porządkowa: autocommit dac9ac4 zapisał przejściowo uszkodzony `tools/dokumenty/tom_PT_AR.py` (48 MB
powtórzeń, +782 tys. linii); ddddb92 przywrócił plik po 24 s, ale obiekt został w historii git.
