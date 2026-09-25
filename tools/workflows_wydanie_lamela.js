export const meta = {
  name: 'wydanie-lamela',
  description: 'Wydanie końcowe: zamrożenie modelu, przeliczenie, regeneracja rysunków i tomów, 3D/www, weryfikacja krzyżowa (4 soczewki), poprawki do czystego wyniku, raport wydania',
  phases: [
    { title: 'Model', detail: 'domknięcie otwartych pozycji + K-13' },
    { title: 'Konstrukcja', detail: 'pętla: zmiany modelu wg REKOMENDACJE_MODEL → pełna analiza → weryfikacja, do 100 %' },
    { title: 'Zamrożenie', detail: 'WYDANIE.json' },
    { title: 'Obliczenia', detail: 'konstrukcja; fizyka/EP/mostki/instalacje' },
    { title: 'Rysunki', detail: 'wszystkie komplety silnikiem ekonomicznym' },
    { title: 'Tomy', detail: 'Tom I + PT-1…4; 3D + www' },
    { title: 'Weryfikacja', detail: 'liczby, prawo, rysunki, woda/izolacje/mostki' },
    { title: 'Poprawki', detail: 'do czystego wyniku' },
    { title: 'Raport', detail: 'README wydania' },
  ],
}
const ROOT = '/home/user/aihouse'
const CTX = `Repozytorium ${ROOT} — projekt budowlany domu jednorodzinnego „Dom LAMELA” (Poznań; działka/MPZP/grunt PRZYKŁADOWE-FIKCYJNE; WT 2002 wg art. 102a PB; RPB Dz.U. 2020 poz. 1609 ze zm.). To jest ETAP WYDANIA: wszystko ma być spójne, kompletne i powtarzalne z jednego źródła.
Źródło prawdy: tools/buduj_model.py → model/*.yaml (schemat docs/SCHEMAT_MODELU.md). Wskaźniki: src/lamela/wskazniki.py. Audyt WT: tools/audyt_wt.py. Obliczenia: src/lamela/obliczenia (konstrukcja: python3 -m lamela.obliczenia.konstrukcja; fizyka/EP: fizyka_energia; instalacje.py; mostki: tools/mostki_budynku.py, tools/katalog_mostkow.py). Rysunki: tools/generuj_widoki.py --arkusze model/arkusze{,_pzt,_is,_ie,_bo,_detale}.yaml (silnik ekonomicznego układu: src/lamela/views/uklad.py; metryki: tools/metryki_arkuszy.py). Tomy: tools/dokumenty/zloz_tom_I.py, tools/dokumenty/tom_PT_{AR,BO,IS,IE}.py → projekt/wydanie/. 3D: src/lamela/pipeline.py (+ tools/render3d). Strona: tools/buduj_www.py → www/dist. Decyzje Inwestora: docs/00_brief_projektowy.md §10. Listy otwartych spraw: docs/20_koncepcja/poprawki_runda2_wejscie.md, docs/20_koncepcja/koncepcja.md §13–14, docs/20_koncepcja/weryfikacja_runda2_V*.md, projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md (jeśli jest), projekt/08_obliczenia/mostki/REKOMENDACJE.md, projekt/*/BRAKI_DANYCH.md.
PYTHONPATH=src dla wszystkich narzędzi. Uruchamiaj testy: tools/test_pipeline.py, tools/test_obliczenia_*.py, tools/test_wskazniki.py, tools/test_arkusze_formaty.py, tools/test_mostki2d.py --szybko.
ZASADY: dane osobowe/uprawnienia/podpisy — [DO UZUPEŁNIENIA] (nigdy nie wymyślaj); dane fikcyjne oznaczone; przepisy cytowane po sprawdzeniu (rejestr docs/10_podstawy_prawne/ lub ELI); żadnych liczb na sztywno w dokumentach; pisz przyrostowo (≤ 150 linii na wywołanie); bez git (commity robi orkiestrator).`

phase('Model')
const modelDom = await agent(`${CTX}

ZADANIE (DOMKNIĘCIE MODELU): (1) wprowadź decyzję Inwestora K-13 (brief §10): zielona ściana z pnączy na lekkiej kratownicy stalowej na elewacji ogrodowej bryły G (ściana S0-02) — kratownica na konsolach z przekładkami termicznymi (mostki punktowe χ ujęte w H_TB), bez przebić hydroizolacji cokołu, pas gruntu/donice z odwodnieniem; ażurowa osłona z lamel wokół jednostki zewnętrznej PC z zachowaniem strefy R290 i przepływu powietrza; zapisz w modelu (element elewacji/wyposażenia zewnętrznego zgodnie ze schematem — jeśli schemat nie ma typu, dodaj minimalne rozszerzenie z opisem w SCHEMAT_MODELU.md i obsługą w rdzeniu tak, by pojawiało się na elewacji S, PZT i w 3D; testy); (2) przeczytaj W CAŁOŚCI docs/20_koncepcja/weryfikacja_runda2_V1.md i weryfikacja_runda2_V2.md (weryfikacja V3 — funkcja — nie została wykonana: wykonaj sam kontrolę kolizji mebli/łuków drzwi/ścian skryptem i obejrzyj rzuty z tools/podglad_modelu.py) i usuń wszystkie uwagi krytyczne i istotne; przejrzyj wszystkie listy otwartych spraw (wymienione w kontekście) i domknij w modelu wszystko, co należy do modelu i jest krytyczne/istotne (w tym rekomendacje konstrukcyjne BO, jeśli wymagają zmian geometrii); każdą decyzję dopisz do koncepcja.md §15 „Rejestr zmian — wydanie”; (3) uruchom walidację (0 błędów), tools/audyt_wt.py (0 niezgodności), tools/test_wskazniki.py, wszystkie testy. NIE zajmuj się zmianami konstrukcyjnymi z projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md — robi to następny etap. Zwróć listę zmian i wskaźniki.`, { label: 'model:domkniecie', phase: 'Model', effort: 'xhigh' })

phase('Konstrukcja')
const KS = { type: 'object', properties: { pozycje_ok: { type: 'number' }, pozycje_wszystkie: { type: 'number' }, zbrojenie_ok: { type: 'number' }, zbrojenie_wszystkie: { type: 'number' },
  docisk_eta: { type: 'number' }, osiadanie_mm: { type: 'number' }, zmiany: { type: 'array', items: { type: 'string' } }, nierozwiazane: { type: 'array', items: { type: 'string' } } },
  required: ['pozycje_ok', 'pozycje_wszystkie', 'zbrojenie_ok', 'zbrojenie_wszystkie', 'docisk_eta', 'osiadanie_mm', 'zmiany', 'nierozwiazane'] }
let konstr = null, kIssues = [], kRound = 0
while (kRound < 3) {
  kRound++
  konstr = await agent(`${CTX}

ZADANIE (KONSTRUKCJA — runda ${kRound}): doprowadź konstrukcję do stanu, w którym WSZYSTKIE pozycje obliczeń statycznych (python3 -m lamela.obliczenia.konstrukcja; moduły pozycje.py, plyta_fundamentowa.py — MES płyty z żebrami na podłożu sprężystym, tarcze.py) i WSZYSTKIE wiersze kontroli zbrojenia (generowanie model/arkusze_bo.yaml → projekt/04_PT_konstrukcja/rysunki, kontrola_zbrojenia.md) są spełnione, docisk do podłoża ≤ nośność, osiadanie ≤ limit, EQU spełnione, brak odrywania bez zakotwienia.
Wejście: projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md (przeczytaj w całości: słupy ŻB z stopami/pogrubieniami pod węzłami A/1, A/3, C/3, D/3; schemat podparcia i zakotwienie B3–B5 (odrywanie B4 −52 kN); przeniesienie obciążenia fasady S1-01 przez B1; filarki muru pod oparciami belek — poszerzenie lub słupki ŻB w murze; elementy niekonstrukcyjne poza wsporniki_plyty; naroże PL-2 — belka krawędziowa lub pogrubienie; jednolita reprezentacja nadproży; blachy czołowe SL1–SL4), a także uwagi z poprzedniej rundy: ${JSON.stringify(kIssues).slice(0, 8000)}
Zmiany geometrii wprowadzaj w tools/buduj_model.py (małymi krokami, walidacja po każdym) — ZACHOWAJ architekturę: słupy i pogrubienia ukryte w ścianach/przegrodach lub w liniach podziałów fasady, bez zmian brył, sylwety „S”, funkcji pomieszczeń i przejść (po zmianie uruchom tools/audyt_wt.py — 0 niezgodności — i obejrzyj rzuty); poprawki biblioteki obliczeń i generatora rysunków BO dozwolone z testami (tools/test_obliczenia_konstrukcja.py, tools/test_rysunki_konstrukcja.py). Każde przyjęcie projektanta [ZAŁ] opisz i uzasadnij (z rzetelnym źródłem lub jako przyjęcie). Dopisz zmiany do docs/20_koncepcja/koncepcja.md §15 i do REKOMENDACJE_MODEL.md (status każdej pozycji). Zwróć strukturę.`, { label: `konstrukcja:${kRound}`, phase: 'Konstrukcja', schema: KS, effort: 'xhigh' })
  const kv = await agent(`${CTX}

JESTEŚ NIEZALEŻNYM, SCEPTYCZNYM WERYFIKATOREM KONSTRUKCJI (runda ${kRound}). NIE poprawiaj. Wynik zespołu: ${JSON.stringify(konstr || {}).slice(0, 6000)}
Sprawdź: (1) odtwórz analizę (python3 -m lamela.obliczenia.konstrukcja, kontrola zbrojenia) i potwierdź liczby; (2) ciągłość ścieżki obciążeń od dachu do gruntu dla każdego elementu (belki, słupy, filarki, wsporniki A, B1 nad przeszkleniem, płyta fundamentowa), stateczność EQU wspornika, zakotwienia przy odrywaniu, przebicie pod słupami, docisk i osiadania; (3) zgodność rysunków BO z obliczeniami (przekroje, zbrojenie, słupy/stopy w rzucie fundamentów); (4) czy zmiany nie zepsuły architektury (rzuty, elewacje, audyt WT); (5) poprawność przyjęć [ZAŁ] i przywołań norm (PN-EN 1990/1991/1992/1996/1997 + NA). Zwróć issues (tylko rzeczywiste problemy krytyczne/istotne/drobne).`, { label: `konstrukcja:weryfikacja:${kRound}`, phase: 'Konstrukcja', effort: 'xhigh', schema: { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['krytyczny', 'istotny', 'drobny'] }, gdzie: { type: 'string' }, problem: { type: 'string' }, poprawka: { type: 'string' } }, required: ['severity', 'gdzie', 'problem', 'poprawka'] } } }, required: ['issues'] } })
  kIssues = (kv && kv.issues ? kv.issues.filter(i => i.severity !== 'drobny') : [])
  const allOk = konstr && konstr.pozycje_ok === konstr.pozycje_wszystkie && konstr.zbrojenie_ok === konstr.zbrojenie_wszystkie && konstr.docisk_eta <= 1.0
  log(`Konstrukcja runda ${kRound}: pozycje ${konstr ? konstr.pozycje_ok + '/' + konstr.pozycje_wszystkie : '?'}, zbrojenie ${konstr ? konstr.zbrojenie_ok + '/' + konstr.zbrojenie_wszystkie : '?'}, uwagi weryfikacji ${kIssues.length}`)
  if (allOk && kIssues.length === 0) break
}

phase('Zamrożenie')
const freeze = await agent(`${CTX}

ZADANIE (ZAMROŻENIE): (a) przelicz katalog mostków na aktualnej geometrii (PYTHONPATH=src python3 tools/mostki_budynku.py) i usuń zależność cykliczną: tabela ψ wpisana w tools/buduj_model.py (_SYM lub podobna) ma być odczytywana z wyników katalogu (projekt/08_obliczenia/mostki/wyniki_mostki.json / zestawienie_mostkow.json) — z bezpiecznym zachowaniem, gdy plik nie istnieje (wartości domyślne PN-EN ISO 14683 i ostrzeżenie); zregeneruj model i sprawdź, że ψ w modelu = ψ z katalogu; (b) uruchom walidację modelu, tools/audyt_wt.py, tools/test_wskazniki.py i testy; jeśli wszystko przechodzi, zapisz model/WYDANIE.json (data, sha256 plików model/*.yaml i tools/buduj_model.py, wskaźniki z lamela.wskazniki, wynik audytu WT, wynik konstrukcji: ${JSON.stringify(konstr || {}).slice(0, 1500)}). Od tej chwili model jest zamrożony (kolejne etapy go NIE zmieniają — jeśli weryfikacja wymusi zmianę, trzeba ponownie zamrozić i przegenerować zależne produkty). Zwróć skrót zawartości WYDANIE.json.`, { label: 'zamrozenie', phase: 'Zamrożenie', effort: 'medium' })
const model = { domkniecie: modelDom, konstrukcja: konstr, zamrozenie: freeze }

phase('Obliczenia')
const obl = await parallel([
  () => agent(`${CTX}

Model zamrożony: ${JSON.stringify(model).slice(0, 3000)}
ZADANIE (KONSTRUKCJA — POTWIERDZENIE): przelicz pełne obliczenia statyczne na zamrożonym modelu (po pętli konstrukcyjnej) i potwierdź (wszystkie pozycje, płyta fundamentowa MES na podłożu sprężystym, ścinanie płyt, schody, belki, nadproża, tarcze jeśli występują), przegeneruj rysunki BO (model/arkusze_bo.yaml → projekt/04_PT_konstrukcja/rysunki) i kontrolę zbrojenia — cel: 100 % pozycji spełnionych, brak [WYMAGA ANALIZY]; jeśli coś nie przechodzi, popraw zbrojenie/przekroje w module rysunków/obliczeń BO (nie w modelu — jeśli konieczna zmiana modelu, opisz precyzyjnie w wyniku jako BLOKADA). Sprawdź zasady konstruowania (załamania wklęsłe, zakotwienia, otuliny). Zwróć wynik kontroli i listę zmian.`, { label: 'obliczenia:BO', phase: 'Obliczenia', effort: 'xhigh' }),
  () => agent(`${CTX}

Model zamrożony: ${JSON.stringify(model).slice(0, 3000)}
ZADANIE (FIZYKA, EP, MOSTKI, INSTALACJE): przelicz na zamrożonym modelu: U przegród, kondensację, katalog mostków (tools/mostki_budynku.py — ψ, f_Rsi ≥ 0,72, H_TB; karty do projekt/08_obliczenia/mostki), EP/EK/EU z PV i bez PV (EP ≤ 70 — wykaż zapas; jeśli brak — BLOKADA z propozycją), obciążenie cieplne i podłogówkę (brak niedoborów), wentylację (bilans), wodę, kanalizację, deszczówkę i retencję, elektrykę (bilans mocy, obwody, ΔU, zwarcia, ryzyko piorunowe, PV z faktycznym rozmieszczeniem). Zapisz wyniki w projekt/08_obliczenia/wydanie/ (md + json) i porównaj z wartościami w koncepcja.md i weryfikacjach — rozbieżności wypisz. Zwróć kluczowe wyniki.`, { label: 'obliczenia:fizyka-instalacje', phase: 'Obliczenia', effort: 'high' }),
])

phase('Rysunki')
const rys = await parallel([
  () => agent(`${CTX}

ZADANIE (RYSUNKI AR, PZT, DETALE): przegeneruj na zamrożonym modelu silnikiem ekonomicznym: AR/PAB (model/arkusze.yaml → projekt/03_PAB/rysunki), PZT (model/arkusze_pzt.yaml → projekt/02_PZT/rysunki), detale (model/arkusze_detale.yaml → projekt/10_PT_architektura/detale; wcześniej tools/mostki_budynku.py wg wyników obliczeń). Zmierz tools/metryki_arkuszy.py (porównaj z docs/30_arkusze/metryki_stan_wyjsciowy.md), obejrzyj KAŻDY arkusz (całość + wycinki), popraw usterki w konfiguracjach lub modułach widoków. Sprawdź, że decyzja K-13 (zielona ściana, osłona PC) jest widoczna na elewacji S, PZT i detalu (jeśli detal potrzebny — dodaj detal mocowania kratownicy do ściany z ETICS z mostkiem punktowym χ). Zwróć metryki i listę arkuszy.`, { label: 'rysunki:AR-PZT-detale', phase: 'Rysunki', effort: 'high' }),
  () => agent(`${CTX}

ZADANIE (RYSUNKI IS, IE): przegeneruj na zamrożonym modelu silnikiem ekonomicznym: IS (model/arkusze_is.yaml → projekt/05_PT_instalacje_sanitarne/rysunki), IE (model/arkusze_ie.yaml → projekt/06_PT_instalacje_elektryczne/rysunki); uaktualnij BRAKI_DANYCH.md (usuń zamknięte, zostaw tylko rzeczywiście otwarte); zmierz metryki, obejrzyj każdy arkusz, popraw usterki. Rysunki BO przegenerowuje zespół konstrukcji — nie ruszaj ich. Zwróć metryki i listę arkuszy.`, { label: 'rysunki:IS-IE', phase: 'Rysunki', effort: 'high' }),
])

phase('Tomy')
const tomy = await parallel([
  () => agent(`${CTX}

ZADANIE (TOMY): uruchom tools/dokumenty/zloz_tom_I.py oraz tools/dokumenty/tom_PT_AR.py, tom_PT_BO.py, tom_PT_IS.py, tom_PT_IE.py na zamrożonym modelu i aktualnych rysunkach; walidatory list kontrolnych (TOM_I, PT_*) — iteruj do statusów OK / DO UZUPEŁNIENIA (dane osobowe) / N/D z podstawą; sprawdź nazwy plików wg zał. 1 RPB, rozmiar ≤ 150 MB, wektorowość, zakładki, numerację stron, spisy treści, metadane; obejrzyj po kilka stron z każdego tomu. Dodaj do wszystkich generatorów tomów wspólny przełącznik (np. zmienna/argument --wydanie-rzeczywiste), który usuwa baner i znak wodny „PRZYKŁAD – NIE DO ZŁOŻENIA” WYŁĄCZNIE wtedy, gdy w danych nie ma już żadnych znaczników [DANE PRZYKŁADOWE – FIKCYJNE] ani [DO UZUPEŁNIENIA] (w przeciwnym razie generator odmawia z listą brakujących pól) — tak, by po uzupełnieniu rzeczywistych danych przez Inwestora i projektantów wydanie do złożenia powstawało jednym poleceniem; opisz to w README wydania. Zwróć listę plików projekt/wydanie/ z rozmiarami i wynikami walidatorów.`, { label: 'tomy', phase: 'Tomy', effort: 'high' }),
  () => agent(`${CTX}

ZADANIE (3D I STRONA): (1) wyeksportuj model 3D z zamrożonego modelu (glTF/GLB + OBJ; jeśli pipeline wspiera — IFC) do projekt/07_model_3D/wydanie/ oraz zestaw renderów (3/4 od SW — hero, od ulicy, lotniczy, aksonometria rozwarstwiona, wnętrze strefy dziennej jeśli możliwe) — z zieloną ścianą K-13; obejrzyj rendery, popraw światło/kadry; (2) przebuduj stronę katalogu tools/buduj_www.py → www/dist (wszystkie liczby z modelu i obliczeń wydania), zrób zrzuty 1440 i 400 px w obu motywach (tools/zrzut_www.py), obejrzyj, popraw usterki; rozmiar strony i zasobów w limitach (strona ≤ 16 MB, pliki ≤ 15 MB, razem ≤ 64 MB). Zwróć listę plików i zrzutów.`, { label: '3D-www', phase: 'Tomy', effort: 'high' }),
])

phase('Weryfikacja')
const VS = { type: 'object', properties: { raport: { type: 'string' }, issues: { type: 'array', items: { type: 'object', properties: {
  severity: { type: 'string', enum: ['krytyczny', 'istotny', 'drobny'] }, gdzie: { type: 'string' }, problem: { type: 'string' }, poprawka: { type: 'string' } }, required: ['severity', 'gdzie', 'problem', 'poprawka'] } } }, required: ['raport', 'issues'] }
const LENSES = [
  { key: 'LICZBY', lens: 'Spójność liczb między modelem, obliczeniami, rysunkami, opisami tomów i stroną www: wybierz ≥ 40 wartości kluczowych (PU i powierzchnie pomieszczeń, pow. zabudowy, PBC, wysokości, kubatura, U, ψ, H_TB, EP z/bez PV, Φ_HL, moc PC, przepływy, średnice, moc przyłączeniowa, zabezpieczenia, klasy betonu, grubości płyt, zbrojenie wybranych pozycji, rzędne, odległości od granic) i sprawdź każdą we wszystkich miejscach, gdzie występuje (PDF tomów — pymupdf, rysunki, www/dist). Każda rozbieżność to błąd.' },
  { key: 'PRAWO', lens: 'Kompletność i zgodność formalno-prawna wydania: listy kontrolne TOM_I i PT_* (uruchom walidatory), RPB § 7, § 14, § 20, § 21, § 23, § 24, zał. 1, PB art. 33, 34, 41 ust. 4a, art. 102a (oświadczenie), BIOZ, geotechnika (Dz.U. 2012 poz. 463), skale rysunków, oznaczenia danych fikcyjnych i pól do uzupełnienia; poprawność KAŻDEGO przywołania aktu prawnego (sprawdź w ELI numer i status) i normy (status aktualna/wycofana — rejestr).' },
  { key: 'RYSUNKI', lens: 'Jakość rysunkowa wszystkich kompletów: obejrzyj każdy arkusz (całość + wycinki gęstych miejsc): kolizje tekstów, czytelność w skali, zgodność oznaczeń z PN (linie, kreskowania, rzędne), kompletność opisów, legend i tabliczek, spójność numeracji arkuszy i spisów, wypełnienie arkuszy i składanie (tools/metryki_arkuszy.py), zgodność rysunków między branżami (osie, rzędne, otwory, piony, przejścia).' },
  { key: 'FUNKCJA', lens: 'Funkcja, ergonomia i jakość architektoniczna na rzutach i elewacjach wydania (projekt/03_PAB/rysunki, podglądy tools/podglad_modelu.py): kolizje drzwi/mebli/ścian (sprawdź skryptem), przejścia, ergonomia kuchni i łazienek (uwagi audytu docs/20_koncepcja/audyt_A3.md — czy rozwiązane), trasy, akustyka, doświetlenie, zgodność z briefem (docs/00_brief_projektowy.md §4, §10) i z sylwetą „S” (wierność szkicowi 00_wejscie/szkic_koncepcyjny.jpg), zielona ściana K-13.' },
  { key: 'WODA-IZOLACJE', lens: 'Wymaganie Inwestora end-to-end: odprowadzenie wody (dachy: wpusty, przelewy awaryjne z rzędnymi, rury spustowe, rynny płyt wysuniętych; teren: spadki, cokół ≥ 0,30 m, odwodnienia liniowe; retencja i niecka; drenaż — decyzja i uzasadnienie), ciągłość izolacji (4 linie) w każdym węźle, mostki termiczne (ψ, f_Rsi, H_TB w EP), hydroizolacja, paroizolacja — zgodność modelu, obliczeń, detali, rysunków IS i opisów PT-AR/PT-IS.' },
]
const ver = (await parallel(LENSES.map(l => () => agent(`${CTX}

JESTEŚ NIEZALEŻNYM, SCEPTYCZNYM WERYFIKATOREM WYDANIA (${l.key}). NIE poprawiaj niczego. Zakres: ${l.lens}
Zapisz raport ${ROOT}/projekt/wydanie/weryfikacja_${l.key}.md i zwróć strukturę (wyłącznie rzeczywiste problemy, z miejscem i poprawką).`, { label: `weryfikacja:${l.key}`, phase: 'Weryfikacja', schema: VS, effort: 'high' })))).filter(Boolean)

phase('Poprawki')
let open = ver.flatMap(v => v.issues.filter(i => i.severity !== 'drobny').map(i => ({ ...i, lens: v.raport })))
let round = 0
const fixes = []
while (open.length && round < 3) {
  round++
  log(`Runda poprawek ${round}: ${open.length} uwag krytycznych/istotnych`)
  const fx = await agent(`${CTX}

ZADANIE (POPRAWKI WYDANIA, runda ${round}): usuń WSZYSTKIE poniższe problemy (oraz zasadne drobne z raportów projekt/wydanie/weryfikacja_*.md). Poprawiaj u źródła (model → obliczenia → rysunki → tomy → www), po każdej zmianie przegeneruj zależne produkty i uruchom testy/walidatory. Problemy: ${JSON.stringify(open).slice(0, 30000)}
Na końcu zapisz projekt/wydanie/poprawki_runda_${round}.md (problem → poprawka → dowód: polecenie i wynik) i zwróć listę NIEROZWIĄZANYCH problemów (jeśli brak — pustą) w formacie JSON {nierozwiazane:[...]}.`, { label: `poprawki:${round}`, phase: 'Poprawki', effort: 'xhigh', schema: { type: 'object', properties: { nierozwiazane: { type: 'array', items: { type: 'string' } }, zmiany: { type: 'array', items: { type: 'string' } } }, required: ['nierozwiazane', 'zmiany'] } })
  fixes.push(fx)
  const re = await agent(`${CTX}

JESTEŚ WERYFIKATOREM KONTROLNYM po rundzie poprawek ${round}. Sprawdź, czy każdy z problemów został rzeczywiście usunięty (odtwórz sprawdzenie), i poszukaj regresji wprowadzonych poprawkami (walidatory, testy, metryki arkuszy, spójność liczb dla 15 losowych wartości). Problemy: ${JSON.stringify(open).slice(0, 20000)}
Zwróć strukturę: issues — tylko nadal otwarte lub nowe problemy krytyczne/istotne.`, { label: `kontrola:${round}`, phase: 'Poprawki', schema: VS, effort: 'high' })
  open = (re && re.issues ? re.issues.filter(i => i.severity !== 'drobny') : [])
}

phase('Raport')
const raport = await agent(`${CTX}

ZADANIE (RAPORT WYDANIA): napisz ${ROOT}/projekt/wydanie/README_WYDANIE.md — rzetelne podsumowanie: zawartość wydania (lista plików z rozmiarami i opisem, tomy, rysunki — liczba arkuszy i papier przed/po optymalizacji, obliczenia, model 3D, strona www), kluczowe parametry budynku (z lamela.wskazniki i obliczeń), spełnienie wymagań (WT/MPZP, EP, mostki, woda), wyniki walidatorów i weryfikacji, UCZCIWA lista ograniczeń i czynności wymaganych przed złożeniem wniosku (dane Inwestora i projektantów z uprawnieniami, podpisy, mapa do celów projektowych od geodety, rzeczywiste badania geotechniczne, uzgodnienia gestorów, wybór wyrobów i DWU, weryfikacja przez uprawnionych projektantów — projekt przykładowy wygenerowany automatycznie NIE może być złożony bez tego), lista pozostałych [DO UZUPEŁNIENIA] (zliczona automatycznie z PDF), instrukcja odtworzenia wydania (polecenia). Pozostałe otwarte problemy weryfikacji: ${JSON.stringify(open).slice(0, 8000)}. Zwróć treść podsumowania (≤ 60 linii).`, { label: 'raport', phase: 'Raport', effort: 'high' })
return { model, obl, rys, tomy, weryfikacja: ver.map(v => ({ raport: v.raport, n: v.issues.length })), fixes, pozostale: open, raport }
