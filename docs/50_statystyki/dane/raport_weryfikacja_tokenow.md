## Weryfikacja tokenów i liczby agentów, sesja d6e847b4

**Wynik:** z 53 sprawdzonych liczb 46 się zgadza. Są 3 rozbieżności powyżej 1%: dwie w raporcie wątku głównego i jedna w szacunku outputu podagentów. Wszystkie sumy tokenów zapisane w transkryptach zgadzają się co do tokena.

Liczyłem własnymi skryptami (`weryfikacja_tokenow*.py`), bez skryptów innych agentów. Porównanie robiłem na tych samych migawkach co raporty:
- wątek główny: odpowiedzi, których pierwsza linia ma timestamp ≤ 08:29:16Z,
- podagenci: ≤ 08:38:50Z.

Źródło: 100 plików JSONL, czyli plik główny oraz 88 plików `agent-*.jsonl` i 11 plików `journal.jsonl` (te ostatnie nie mają usage). W repozytorium niczego nie zmieniałem; git używałem tylko do odczytu (rev-list, log, ls-tree, show).

### 1. Reguła deduplikacji (sprawdzona na danych)
- **Wątek główny:** 1319 linii assistant daje 746 message.id i tyle samo requestId. Rozkład linii na id: 349 / 250 / 125 / 16 / 5 / 1. We wszystkich 397 id zapisanych w kilku liniach usage jest identyczne. Wszystkie 746 odpowiedzi mają końcowe usage (z `output_tokens_details`), więc output w wątku głównym jest dokładny.
- **Podagenci, pola wejściowe:** input, cache_read i cache_creation (z rozbiciem 5m/1h) są identyczne we wszystkich liniach danego id. Sprawdzone na 6331 id z wieloma liniami.
- **Podagenci, output:** `output_tokens` rośnie monotonicznie w 1953 id i ostatnia linia ma zawsze maksimum. Nie znalazłem ani jednego spadku.
- **Przyjęta reguła:** usage liczę raz na message.id, z linii o największym output_tokens (to zawsze ostatnia linia). Dodatkowo deduplikuję globalnie między plikami.
- **Jedno id w dwóch plikach:** msg_011CfPVW3ohSESrTEdG7pAvt występuje w obu plikach agenta a3a8ae3b. Bez globalnej deduplikacji cache_read byłby zawyżony o 502 256 tokenów.
- **Pozostałe kontrole:**
  - requestId odpowiada message.id 1:1.
  - Pole `iterations` ma zawsze 1 element.
  - Serwerowych web_search i web_fetch jest 0.
  - Model jest jeden: claude-opus-5-5 (wszystkie 17 754 linie assistant).
- **Output podagentów jest niepełny:** tylko 2486 z 8375 odpowiedzi (29,7%) ma końcowe usage. Pozostałe 5889 mają stop_reason=null i usage z początku strumienia (razem 66 990 tokenów output). Output podagentów z transkryptów to więc tylko dolna granica.

### 2. Agenci (pliki)
Stan na migawkę podagentów (08:38:50Z):
- **Samodzielni:** 15. Na górnym poziomie jest 16 plików `agent-*.jsonl`, ale 15 ma plik meta.json. Szesnasty to druga egzekucja agenta przepływu a3a8ae3b ("synteza"), bez meta.json.
- **Agenci przepływów:** 68 plików w 11 katalogach wf_*.
- **Razem:** 83 unikalne agentId i 84 egzekucje.
- **Kopia syntezy:** potwierdziłem ją po drzewie parentUuid. Rozwidlenie następuje o 03:42:39 (wiadomość SendMessage). Kopia ma 147 odpowiedzi i działała od 03:42:39 do 04:24:18.
- **Stan teraz (~09:01Z):** 72 pliki agentów przepływów i 87 unikalnych agentId. Przybyły 4 pliki w przepływie statystyk.

### 3. Tokeny na migawkach (wszystko claude-opus-5-5)

| Grupa | Odpowiedzi | Input | Output zapisany | cache_read | Zapis 5m | Zapis 1h |
|---|---|---|---|---|---|---|
| Wątek główny | 746 | 1 706 | 694 008 (w tym thinking 236 043) | 322 522 223 | 0 | 1 677 969 |
| Samodzielni (15) | 2 807 | 5 622 | 1 547 495 | 1 125 574 262 | 19 272 452 | 0 |
| Przepływy (68) | 5 421 | 10 842 | 1 566 360 | 1 319 323 396 | 29 120 043 | 0 |
| Kopia syntezy | 147 | 294 | 66 122 | 78 718 809 | 655 012 | 0 |
| **Razem** | **9 121** | **18 464** | **3 873 985** | **2 846 138 690** | **49 047 507** | **1 677 969** |

- Wywołania narzędzi: wątek główny 747, podagenci 9 006.
- Stan teraz (~09:01Z): 9 404 odpowiedzi, z tego 779 w wątku głównym.

### 4. Rozbieżności powyżej 1%
1. **Raport główny, SendMessage.**
   - Zgłoszono: „do 9 agentów; a5045de9 dostał 7”.
   - Poprawnie: 17 wiadomości do 8 agentów. a5045de9 dostał 6, a3a8ae3b 3, a9f2ed8b 3, pięciu pozostałych po 1.
   - Przyczyna: błąd przepisania. Plik main.json tego samego agenta ma poprawne wartości, a raport podagentów też podaje je poprawnie.
2. **Raport główny, sumy z powiadomień agentów.**
   - Zgłoszono: tool_uses 3618 i duration_ms 82 098 091 (≈ 22,8 h).
   - Poprawnie: tool_uses 3070 i duration_ms 72 319 469 (≈ 20,1 h).
   - Przyczyna: drugie powiadomienie a5045de9 jest narastające (548→549 wywołań, 9 778 622→10 054 052 ms), więc pierwsze liczy się podwójnie.
   - Kontrola: 3070 = 2923 wywołania w transkryptach 15 samodzielnych agentów + 147 wywołań kopii syntezy.
3. **Raport podagentów, szacowany output.**
   - Zgłoszono: 12,28 mln (thinking 5,59 mln), koszt ≈ $996.
   - Metodę raportu odtworzyłem z różnicą 0,05%: 12 286 215 tokenów, współczynniki 0,2371 i 0,5562.
   - Problem: metoda zakłada stały przelicznik tokenów thinking na znak podpisu. W danych przelicznik rośnie od ~0,05 do ~0,33 wraz z długością podpisu. Odpowiedzi bez końcowego usage mają dłuższe podpisy (średnio 3155 znaków wobec 2019).
   - Mój estymator warstwowy daje **12,96 mln** output (thinking 6,34 mln). Walidacja krzyżowa na dwóch połowach agentów: 1,017 i 0,986.
   - Wiarygodny zakres to 12,3–13,2 mln, a 3,18 mln to twarda dolna granica.
   - Koszt podagentów wychodzi ≈ **$1 009**; przy samym zapisanym outputcie $813,63.

### 5. Drobne uwagi (poniżej 1%)
- **Mediana kontekstu:** zgłoszone 436 313 to median_high. Mediana z 746 wartości wynosi 436 174,5.
- **Commity do 08:29:16Z:** jest ich 396. Zgłoszone 395 to stan na ostatnią linię transkryptu (08:28:04).
- **Wspólne id w plikach syntezy:** raport podagentów pisze, że między egzekucjami nie powtarza się żaden message.id. Po podziale na gałęzie to prawda, ale oba pliki mają 1 wspólne id. Raport je zdeduplikował.
- **Czas aktywności:** samodzielni 1163,9 min (raport 1163,7), przepływy 1778,3 min (raport 1778,2).
- **Agent a5045de9:** 546 odpowiedzi i 196 557 890 tokenów cache_read, zgodnie z raportem.

### 6. Koszt porównawczy (tylko arytmetyka)
Liczyłem według stawek podanych w raportach: $4 input, $20 output, $0,20 cache read, $5 zapis 5m, $8 zapis 1h za 1 mln tokenów. Samych stawek nie weryfikowałem.

| Pozycja | Koszt |
|---|---|
| Wątek główny | $91,82 (bez cache $1 310,69) |
| Podagenci, output zapisany | $813,63 |
| Podagenci, metoda raportu | $995,75 |
| Podagenci, metoda warstwowa | $1 009,23 |
| **Cała sesja** | **≈ $1 101**, dolna granica $905,45 |

### 7. Repozytorium, wyrywkowo na HEAD d4716b00
Wszystkie sprawdzone liczby zgadzają się z raportem:

| Miara | Wartość |
|---|---|
| Commity (0 merge'y) | 402 |
| Commity do 08:30:00Z | 397 |
| Autocommity | 287 |
| Pliki śledzone | 1300 |
| Pliki .py / .png | 235 / 547 |
| Rozmiar śledzony | 350,45 MB (350 451 895 B) |
| Funkcje `def test` | 158, w podziale 14/26/24/24/28/28/12/2 |
| Plansze raport_*.png | 50, numery 01–50 |

Pliki są w `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/`:
- weryfikacja_tokenow.json – wynik, w tym porównanie wszystkich 53 liczb, sumy per plik i per przepływ, szacunki i koszt,
- weryfikacja_tokenow_raw.json oraz raw2 do raw7 – wyniki pośrednie,
- weryfikacja_tokenow.py, weryfikacja_tokenow_2.py do _7.py oraz weryfikacja_tokenow_zapis.py – skrypty.