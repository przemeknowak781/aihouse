CENY API ANTHROPIC DO WYCENY SESJI (odczyt 2026-09-25 ok. 08:41–08:43 UTC; to migawka, transkrypty nadal rosną)

1. MODELE W TRANSKRYPTACH
- Grep `"model":"` o 08:43:24Z: plik główny d6e847b4-….jsonl to 1359 × "claude-opus-5-5". Katalog subagents (rekursywnie, 96 plików .jsonl plus pliki .meta.json) to 16028 × "claude-opus-5-5". Przebieg o ok. 08:41Z dał 1354 / 15950.
- Parsowanie JSON (pole message.model) w ceny_api.py dało:
  - plik główny: 1359 linii i 768 unikalnych message.id,
  - subagenty: 16046 linii i 8468 unikalnych message.id.
  Różnica między liczbą linii a liczbą id potwierdza, że jedną odpowiedź API zapisano w kilku liniach.
- Wniosek: występuje WYŁĄCZNIE claude-opus-5-5. Nie ma Sonnet, Haiku ani Fable.
- Pola usage we wszystkich liniach:
  - speed jest "standard" albo go brak, więc tryb fast nie był używany,
  - service_tier jest zawsze "standard", więc nie było Batch API,
  - inference_geo jest zawsze "not_available", więc nie ma mnożnika 1.1x za US-only,
  - server_tool_use.web_search_requests sumuje się do 0 (licząc max na message.id).
- Nie da się ustalić, czy wyszukiwania narzędziem WebSearch z Claude Code są rozliczane poza tymi polami.

2. CLAUDE OPUS 5.5 (claude-opus-5-5): jest na oficjalnej stronie, więc wycena NIE jest przybliżeniem
Ceny w USD za 1 mln tokenów (MTok):
- input: $4
- output: $20 (thinking_tokens liczą się jako output)
- zapis do cache 5 min: $5 (1.25x)
- zapis do cache 1 h: $8 (2x)
- odczyt z cache (cache hit): $0.20 (0.05x, wyjątkowo; standardowo jest 0.1x)
- Batch (−50%): $2 wejście / $10 wyjście
- Tryb fast: $8 / $40. Ceny cache w trybie fast wyliczyłem sam, strona ich nie podaje wprost: $10 / $16 / $0.40.
- Długi kontekst powyżej 200k: BRAK dopłaty.
- US-only: mnożnik 1.1x.
- Web search: $10 za 1000 wyszukiwań.

Cytaty z https://platform.claude.com/docs/en/about-claude/pricing (docs.claude.com/en/docs/about-claude/pricing przekierowuje tam kodem 302):
- "| Claude Opus 5.5 | $4 / MTok | $5 / MTok | $8 / MTok | $0.20 / MTok<sup>2</sup> | $20 / MTok |"
- "2 Cache hits and refreshes on Claude Opus 5.5 are priced at 0.05x the base input price."
- Fast mode: "| Claude Opus 5.5 | $8 / MTok | $40 / MTok |"
- "Fast mode pricing applies across the full context window, including requests over 200k input tokens."
- Batch: "| Claude Opus 5.5 | $2 / MTok | $10 / MTok |"
- "The Batch API allows asynchronous processing of large volumes of requests with a 50% discount on both input and output tokens."
- "Claude 4.6 and later models ... include the full 1M token context window at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.)"
- "specifying US-only inference through the `inference_geo` parameter incurs a 1.1x multiplier on all token pricing categories"

Potwierdzenie z https://claude.com/pricing (www.anthropic.com/pricing przekierowuje tam kodem 301):
- "Opus 5.5 … Prompt caching Read $0.20 / MTok Write $5 / MTok Input $4 / MTok Output $20 / MTok"
- "Get up to 2.5x faster speeds with fast mode for Opus 5.5 at 2x standard pricing."
- "Prompt caching pricing reflects 5-minute TTL."

ID modelu potwierdza https://platform.claude.com/docs/en/models/overview: `claude-opus-5-5` = Claude Opus 5.5.

3. CENY PORÓWNAWCZE
Kolejność: input / zapis cache 5 min / zapis cache 1 h / odczyt cache / output, w USD za MTok. Pełną tabelę 18 modeli sparsowałem z oficjalnej strony do JSON.

| Model | input | zapis 5 min | zapis 1 h | odczyt | output |
|---|---|---|---|---|---|
| Fable 5.1 / Mythos 5.1 | 10 | 12.50 | 20 | 0.25 | 50 |
| Opus 5, 4.8, 4.7, 4.6, 4.5 | 5 | 6.25 | 10 | 0.50 | 25 |
| Opus 4.1 / 4 | 15 | 18.75 | 30 | 1.50 | 75 |
| Sonnet 5 | 2 | 2.50 | 4 | 0.20 | 10 |
| Sonnet 4.6 / 4.5 | 3 | 3.75 | 6 | 0.30 | 15 |
| Haiku 4.5 | 1 | 1.25 | 2 | 0.10 | 5 |

- Sonnet 5, przypis 3: stawka $2/$10 jest teraz ceną standardową, a zapowiadana podwyżka do $3/$15 od 1.09.2026 nie nastąpi.
- Zastrzeżenie przy porównaniach: "Claude 4.7 and later models … use a newer tokenizer … approximately 30% more tokens for the same text … Claude Sonnet 4.6 and earlier models use the previous tokenizer". Wycena tych samych tokenów cenami Sonnet 4.6, Haiku 4.5 lub Opus 4.6 i starszych jest więc przybliżeniem.

4. PLANY SUBSKRYPCYJNE (USD, bez podatku: "Prices shown don't include applicable tax.")
Źródło: https://claude.com/pricing, chyba że zaznaczono inaczej.
- Free: "$0".
- Pro: "$17 Per month with annual subscription discount ($200 billed up front). $20 if billed monthly."
- Max: na claude.com/pricing jest tylko "From $100 Per month … Choose 5x or 20x more usage than Pro". Kwoty dla obu wariantów podaje https://support.claude.com/en/articles/11049741-what-is-the-max-plan:
  - "Max 5x: $100 per month"
  - "Max 20x: $200 per month"
  - Rozliczenie: "Both options are billed monthly."
- Team:
  - standard: "$20 Per seat / month if billed annually. $25 if billed monthly."
  - premium: "$100 … annually. $125 if billed monthly."
- Enterprise: "US$20/seat/month, billed annually" plus "usage at API rates".
- "Claude Code is included in all paid plans. It shares the same usage limits as the rest of your plan … you can also switch to pay-as-you-go API credits through a Console account."
- Limity planów to okna 5-godzinne plus limity tygodniowe, nie wyrażone w tokenach. Nie da się więc przeliczyć tokenów sesji na „zużycie planu”.
- Z samych danych cenowych nie da się też ustalić, czy ta sesja była rozliczana w planie, czy per token.

5. SIEĆ
Strony odpowiadały przez proxy kodem HTTP 200, z włączoną weryfikacją TLS. Sprawdzanie statusu proxy nie było potrzebne.

Pliki w /tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/:
- ceny_api.json: wynik, z cytatami, URL-ami i sumami sha256 kopii stron,
- ceny_api.py: skrypt, który go generuje,
- kopie źródeł: raw_platform_pricing.md, raw_claude_com_pricing.html, claude_com_pricing_text.txt, raw_support_max_plan.html, raw_models_overview.md.

Nie modyfikowałem niczego w /home/user/aihouse.