## Podagenci i przepływy: statystyki sesji d6e847b4 (migawka z 2026-09-25T08:38:50Z)

Część przepływów nadal działa, więc liczby opisują stan na chwilę migawki. Liczby dotyczą wyłącznie podagentów i przepływów, bez wątku głównego. Skrypt `analiza_podagentow.py` tylko czyta dane sesji. W repozytorium niczego nie zmieniałem.

### 1. Ile było agentów i przepływów

**Samodzielni agenci:** 15.
- W wątku głównym jest 15 wywołań narzędzia Agent i 15 transkryptów `subagents/agent-*.jsonl` z plikiem `.meta.json`.
- Wszyscy mają powiadomienie `completed`. Agent a5045de9 ma dwa takie powiadomienia, bo po pierwszym zakończeniu wznowiła go kolejna wiadomość.

**Agenci przepływów:** 68 unikalnych agentId, czyli 68 plików `workflows/wf_*/agent-*.jsonl`.

**Dodatkowa egzekucja agenta syntezy (a3a8ae3b05a6e1fbd):**
- SendMessage z 03:42:38 wznowił drugą kopię tego agenta. Kopia pracowała równolegle z oryginałem od 03:42:39 do 04:24:18.
- Transkrypt jest rozłożony na dwa pliki ze wspólnym początkiem. Rozdzieliłem go po drzewie parentUuid.
- Między egzekucjami nie powtarza się żaden message.id.

**Razem:** 83 unikalne agentId i 84 egzekucje.

**Przepływy:** 11 identyfikatorów runId i 12 wywołań narzędzia Workflow. Jeden runId ma dwa uruchomienia, bo był wznawiany.

Źródła godzin startu i końca: wynik wywołania Workflow (Task ID i katalog transkryptów), TaskStop i powiadomienia `<\task-notification>`. Fazy pochodzą z meta.phases w skryptach.

| Przepływ | runId | taskId | Start–koniec (UTC) | Czas zegarowy [min] | Agenci | Status |
|---|---|---|---|---|---|---|
| rejestr-prawny-A | wf_88c0988f-4a5 | w3j43xp0k | 23:27–00:41 | 73,6 | 8 | zakończony |
| rejestr-norm-B | wf_0e783e5d-4ab | wqihva7xz | 23:28–01:14 | 105,5 | 8 | zakończony |
| koncepcja-panel (podejście 1) | wf_725a3592-fa1 | whby2u54e | 23:30–23:33 | 3,8 | 2 | zatrzymany (TaskStop) |
| koncepcja-panel (podejście 2) | wf_44634517-034 | we1mlli53 + wy0zakhf7 (wznowienie) | 23:37–05:20 | 342,1 (145,5 + 196,2) | 12 | zakończony |
| mostki-2d-solver | wf_a0d51b50-592 | wmqylk5tf | 01:58–03:42 | 103,3 | 5 | zakończony |
| poprawki-runda2 | wf_10e1a801-dd6 | wbied9nrs | 05:21–07:13 | 111,6 | 5 | zatrzymany (TaskStop) |
| arkusze-ekonomiczne | wf_dad224e5-cd8 | wf4hulepa | od 05:38 | ≥180 | 7 | trwa |
| opisy-tom-I | wf_ce63599a-15f | w9d1ib8kz | 06:33–08:05 | 92,1 | 6 | zakończony |
| opisy-PT | wf_c5f7e298-4b9 | wifid07x3 | od 06:33 | ≥125 | 10 | trwa |
| wydanie-lamela | wf_a8783476-2a1 | wzwhv71tc | od 07:13 | ≥85 | 2 | trwa |
| statystyki-sesji (ten przepływ) | wf_6070a5f0-602 | w4z4krxmz | od 08:27 | ≥11 | 3 | trwa |

Fazy przepływów:
- **rejestry A i B:** Badanie, Weryfikacja.
- **koncepcja-panel:** Warianty, Ocena, Synteza, Audyt, Poprawki.
- **mostki:** Budowa, Weryfikacja, Poprawki, Demo.
- **poprawki-runda2:** Funkcja, Fizyka i woda, Weryfikacja, Domknięcie.
- **arkusze:** Pomiar, Silnik, Zastosowanie, Weryfikacja, Poprawki.
- **tom I i PT:** Opisy, Tom(y), Weryfikacja, Poprawki.
- **wydanie:** 9 faz, od Modelu do Raportu.

### 2. Tokeny i koszt

**Reguła deduplikacji (sprawdzona na danych):**
- 15 843 linie asystenta dają 8 375 unikalnych message.id.
- Pola input i cache są identyczne we wszystkich liniach danego id (0 niespójności).
- Pole output_tokens w obrębie jednego id bywa różne. Dlatego z każdego id biorę usage z linii o największym output_tokens.
- Wszystkie odpowiedzi pochodzą z modelu claude-opus-5-5. Wszystkie zapisy pola speed mają wartość "standard", więc nie było trybu fast.

**Najważniejsze zastrzeżenie: output w transkryptach jest zaniżony.**
- Tylko 2 486 z 8 375 odpowiedzi (29,7%) ma końcowe usage z polem `output_tokens_details`. Wszystkie te odpowiedzi mają stop_reason "tool_use".
- Pozostałe mają tylko usage z początku strumienia, z output_tokens zwykle od 2 do 24. Suma output z transkryptów to więc tylko dolna granica.
- Brakujący output oszacowałem, i to wprost opisuję. Metoda:
  - 0,557 tokena na znak widocznej treści (tekst plus JSON wejścia narzędzi);
  - 0,2366 tokena na znak podpisu bloku thinking (sam tekst thinking jest pusty).
- Współczynniki skalibrowałem na 2 486 odpowiedziach z pełnym usage.
- Walidacja krzyżowa na dwóch połowach agentów dała stosunek sumy oszacowanej do rzeczywistej 0,987 i 1,012.
- Rozrzut błędu dla pojedynczego agenta wynosi od −14% do +7% (percentyle p10–p90).
- Alternatywne oszacowanie regresją daje 13,01 mln tokenów output.

| Grupa | Odpowiedzi API | Wywołania narzędzi | Input | Output zapisany (dolna granica) | Output szacowany (w tym thinking) | cache_read | cache_write 5m / 1h |
|---|---|---|---|---|---|---|---|
| Samodzielni (15) | 2 807 | 2 923 | 5 622 | 1,55 mln | 5,30 mln (2,05 mln) | 1 125,6 mln | 19,27 mln / 0 |
| Przepływy (68) | 5 421 | 5 936 | 10 842 | 1,57 mln | 6,79 mln (3,45 mln) | 1 319,3 mln | 29,12 mln / 0 |
| Kopia syntezy | 147 | 147 | 294 | 0,07 mln | 0,19 mln (0,09 mln) | 78,7 mln | 0,66 mln / 0 |
| **Razem** | **8 375** | **9 006** | **16 758** | **3,18 mln** | **12,28 mln (5,59 mln)** | **2 523,6 mln** | **49,05 mln / 0** |

Wywołania narzędzi według nazwy: Bash 6 862, Read 1 113, Write 290, WebSearch 204, Edit 193, WebFetch 164 i pozostałe.

**Uwaga do metryk harnessu.** Pola `tokens` i `totalTokens` w plikach wf_*.json oraz `subagent_tokens` w powiadomieniach to rozmiar kontekstu ostatniej odpowiedzi, a nie zużycie narastające. Dla agentów przepływów zgodność wynosi dokładnie 1,000. Przykład: dla agenta a87415027562c59a6 powiadomienie podaje 65 384 tokeny, a agent odczytał z cache 63,5 mln tokenów. Tych pól nie wolno używać do liczenia kosztu.

**Koszt porównawczy (pomocniczo, do sprawdzenia przez agenta od cennika).**
- Cennik claude-opus-5-5 wziąłem z pakietu skill claude-api (`shared/models.md:77` i `shared/model-migration.md:2023`): $4 za MTok input, $20 za MTok output, $0,20 za MTok odczytu cache.
- Stawki zapisu cache ($5 za 5 min, $8 za 1 h) źródło wyprowadza z mnożników i oznacza jako do potwierdzenia.
- Koszt podagentów przy szacowanym output: **ok. $996**. Przedział od $814 (output zapisany) do $1 010 (oszacowanie regresją).
- Składniki: odczyt cache $505, output $246, zapis cache $245, input $0,07.
- Podział: samodzielni $428, przepływy $545, przypadkowa kopia syntezy $23.

**Najdłuższy i zarazem najdroższy agent:** a5045de9ee0554cc8, „Build structural drawings generator”, samodzielny.
- Pracował od 04:08:17 do 06:55:51, czyli 167,6 min.
- 546 odpowiedzi API i 549 wywołań narzędzi.
- cache_read 196,6 mln tokenów, szacowany output 0,62 mln, koszt ok. $65 (przedział $59–65).
- Dostał 6 wiadomości korygujących od orkiestratora i przeszedł 1 kompakcję kontekstu.
- Kolejne pod względem kosztu: a82012b7 (strona www, 113,5 min, $41), a9f2ed8b (detale, 99,6 min, $37), a076389c (PZT, 89,9 min, $35) i af672122 (model:domkniecie, 75,8 min, $33).

### 3. Iteracje

**Role 68 agentów przepływów:** produkcja 34, weryfikacja/audyt/kontrola 20, poprawki 11, sędziowie 3.

**Rundy weryfikacja → poprawki w poszczególnych przepływach:**
- **rejestr A i B:** po jednej rundzie. To 4 pary badanie→weryfikacja w każdym przepływie; weryfikatorzy sami nanosili korekty w plikach.
- **koncepcja-panel:** 1 runda (audyt A1–A3 z 51 uwagami, w tym 2 krytycznymi, potem 1 agent poprawek). Wcześniej była jedna faza oceny: 3 sędziów, potem synteza.
- **mostki:** 1 runda (20 uwag, 0 krytycznych).
- **tom I:** 1 runda.
- **PT:** 1 runda z 4 równoległymi agentami poprawek. Agent poprawek AR jeszcze pracuje.
- **poprawki-runda2:** poprawki, potem weryfikacja V1–V3. Weryfikacja V3 została przerwana, a faza Domknięcie nie ruszyła.
- **arkusze:** tylko poprawka silnika według zgłoszeń zespołów. Weryfikacja jeszcze nie ruszyła.
- **wydanie:** trwa 1. runda pętli Konstrukcja. Skrypt dopuszcza do 3 rund konstrukcja↔weryfikacja i do 3 rund poprawki↔kontrola.

Łącznie 7 przepływów ma co najmniej jedną rundę. Sam model przeszedł trzy fale poprawek: rundę 1 w panelu koncepcji, rundę 2 w przepływie poprawki-runda2 i domknięcie w przepływie wydania.

**Ponowne uruchomienia i wznowienia.** Panel koncepcji uruchamiano trzy razy:
1. whby2u54e zatrzymany po 3,8 min, bo użytkownik zmienił założenie: element D to elewacja w kształcie „S”, a nie płyta tarasu.
2. we1mlli53 z nowym runId, zatrzymany po 145,5 min, bo wariant W3 zawiesił się na około 86 min.
3. wy0zakhf7, wznowienie z `resumeFromRunId`. Warianty W1 i W2 przyszły z cache, a W3 poszedł od nowa.

Wynika z tego, że W1 i W2 wykonano po dwa razy, a W3 dwa razy (w pierwszym podejściu W3 czekał tylko w kolejce).

**Pozostałe iteracje:**
- Wszystkie trzy zatrzymania (whby2u54e, we1mlli53, wbied9nrs) wykonano przez TaskStop.
- Każdy agent przepływu ma attempt = 1, więc nie było automatycznych ponowień.
- Orkiestrator wysłał 17 wiadomości SendMessage do 8 agentów: a5045de9 6 razy, a9f2ed8b 3 razy, synteza 3 razy, pozostali po razie.
- Kompakcję kontekstu przeszło 5 samodzielnych agentów, każdy po razie.

**Równoległość (wyliczona z przedziałów start–koniec):**
- Maksymalnie **9 agentów naraz**, po raz pierwszy o 04:08:41. Poziom 9 wrócił o 04:22:09, 06:48:07 i 06:52:46.
- Łącznie 23,3 min przy 9 agentach i 97,6 min przy co najmniej 8.
- Sami agenci przepływów: maksymalnie 7 naraz.
- W żadnym przepływie nie pracowało więcej niż 2 agentów jednocześnie, także tam, gdzie skrypt uruchamia `parallel()` na 3–5 agentów. Na przykład ten przepływ statystyk zaplanował 5 agentów, a naraz działało 2. Wygląda to na limit harnessu wynoszący 2 agentów na przepływ.

### 4. Czas pracy agentów wobec czasu sesji

- **Sesja:** od 2026-09-24T23:07:30Z (pierwszy wpis wątku głównego) do migawki, czyli **571,3 min (9,52 h)**.
- **Suma czasów aktywności agentów:** **2 983,4 min (49,7 h)**. Samodzielni 1 163,7 min, przepływy 1 778,2 min, kopia 41,7 min.
- **Współczynnik równoległości:** 5,22 względem całej sesji i 5,41 względem 551,2 min, w których pracował co najmniej jeden agent.
- **Rozkład czasu według liczby agentów:** 3 agentów przez 101 min, 4 przez 71, 5 przez 120, 6 przez 112, 7 przez 44, 8 przez 74, 9 przez 23.

### 5. Kompletność danych i luki

**Zgodność źródeł:**
- 15 wywołań Agent odpowiada 15 transkryptom i 15 powiadomieniom `completed`.
- 12 wywołań Workflow odpowiada 12 plikom `tasks/w*.output` i 11 katalogom transkryptów.
- 5 przepływów ma powiadomienie `completed`, 3 zatrzymano przez TaskStop, 4 trwają.

**Powiadomienia a pliki agentów:**
- Liczba agentów w powiadomieniach zgadza się z plikami: 8, 8, 5, 6.
- Wyjątek: przepływ wy0zakhf7 podaje 11 agentów, a plików jest 12. Dodatkowy plik to W3 zabity w pierwszym uruchomieniu.
- Liczby wywołań narzędzi zgadzają się co do sztuki: 715, 1141, 298 i 610. Dla wy0zakhf7 powiadomienie podaje 531, co daje 674 po dodaniu 126 wywołań W1 i W2 z pierwszego uruchomienia oraz 17 wywołań zabitego W3.

**Wcześniejsze części sesji:**
- Wszystkie 57 identyfikatorów agentów wspomnianych w wątku głównym ma transkrypty.
- Wszystkie 16 dowiązań `tasks/a*.output` wskazuje na istniejące pliki.
- Transkrypt główny obejmuje sesję od początku. Nie brakuje agentów z wcześniejszych części sesji.
- W transkrypcie głównym są 2 wpisy compact_boundary. Wątek główny wspominał o trzech kompakcjach; tego nie wyjaśniałem.

**Rzeczywiste luki:**
1. Output_tokens jest niepełny dla 70% odpowiedzi (opis i metoda szacunku w punkcie 2).
2. Cztery trwające przepływy nie mają jeszcze pliku wf_*.json, więc dane o nich pochodzą z journal.jsonl i transkryptów.
3. Wiersze agentów, które jeszcze pracują, w tym tego raportu, rosną z każdą minutą.

Plik z pełnymi wynikami, w tym tabelą 84 egzekucji z tokenami, kosztem, czasem, narzędziami i statusem, per przepływ, iteracjami, powiadomieniami i estymatorem:
`/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/podagenci.json`

Skrypt, który go tworzy:
`/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/analiza_podagentow.py`