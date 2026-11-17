export const meta = {
  name: 'rewizja-v13-audyt',
  description: 'Spec revision v1.3 implementing the structural & functional audit (41 findings + 10 critic gaps) with coordinator decisions D-1..D-5; 3 sequential implementers, 3-lens verification with audit-closure check, fix',
  phases: [
    { title: 'Revise', detail: 'A garage/segment/fire services/parking/MDS → B ground floor/hall/conference/structure → C geotech/technology/phasing/cost + validation' },
    { title: 'Verify', detail: 'fire+evacuation, structure+geotech+water, function+parking+cost; closure table for every audit ID' },
    { title: 'Fix', detail: 'apply confirmed problems, re-run the chain and tables' },
  ],
}
const ROOT = '/home/user/aihouse/umwd'
const PY = '/home/user/aihouse/.venv-render/bin/python -I'
const V12B = (args && args.v12b) ? String(args.v12b) : '(brak streszczenia v1.2b – przeczytaj sekcję v1.2b w rejestrze)'
const CTX = `Projekt konkursowy „BRAMA I LATARNIA” (siedziba UMWD i Sejmiku Województwa Dolnośląskiego, Wrocław, narożnik Mazowiecka / Wybrzeże J. Słowackiego). Katalog ${ROOT}. Python: ${PY}. Nie commituj (robi to sesja główna).
INTEGRALNOŚĆ (bezwzględnie): konkurs jest rozstrzygnięty; NIE szukaj i NIE używaj informacji o pracach nagrodzonych/konkurencyjnych w TYM konkursie.
STAN WEJŚCIOWY: specyfikacja v1.2 + decyzje v1.2b – model/koncepcja.json, docs/20_koncepcja/koncepcja_wybrana.md, kondygnacja_S2.md/.json, rejestr docs/20_koncepcja/rejestr_poprawek_v1_1.md (kolejność skryptów łańcucha: _s2_geometria → _s2_sala → _s2_ewakuacja → _s2_rzut → _v12_trzony → _v12_koszt → _v12_scalenie --zapisz → _v12b_decyzje → tools/tabele_konkursowe.py; NIE uruchamiaj _rewizja_json.py --zapisz). Streszczenie v1.2b: ${V12B.slice(0, 6000)}
AUDYT DO WDROŻENIA: docs/90_audyt/audyt_konstrukcja_funkcja.md – rozdz. 1 (41 ustaleń z poprawkami), 2 (szczegóły), 5.1–5.6 (decyzje, kolejność, macierz, konflikty K-1…K-19 z rozstrzygnięciami, bilans miejsc, koszt), 6 (luki L-01…L-10). Skrypty obliczeń audytu: /tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/audyt_kf/ (redakcja/spojnosc.py, krytyk/k*.py).
DECYZJE KOORDYNATORA (wiążące):
D-1 rampa uliczna dwukierunkowa 5,5 m (6,0 m w świetle odbojów), brama ≥ 6,0 m cofnięta 1,5–2,0 m za lico, żaden słup w świetle bramy (belki krawędziowe), poszerzenie parteru segmentu o 1,5 m jeśli potrzebne; obsługa −2 RAMPĄ wewnętrzną dwukierunkową 6,0 m (nie dźwig samochodowy), z rozwiązaniem K-11 (GPC ≥ 95 m²), K-12 (centrala S / bilans kond. 1), K-17 (słup elewacji wsch. w grubości ściany). Dźwig samochodowy tylko jeśli udowodnisz liczbowo, że rampa jest niewykonalna.
D-2 garaż: samoczynna wentylacja oddymiająca kanałowa (limit dojścia 60 m), bez tryskaczy.
D-3 parter skrzydła: pakiet G1 (przejście hala–foyer 2,95 m, sala 200 przy bramie, sala 80 przy foyer, po 2 wyjścia ≥ 5 m z sali 80 i z każdej połowy sali 200, drzwi zewn. tylko na dziedziniec, widownia w blokach ≤ 16), obniżenie posadzki M1 do ok. 118,82–118,85 (wejście bez progu z bramy), uskok stropu nad −1 pod bramą (≤ 118,45), strop pasa dziedzińca 119,15 → 119,08 ze spadkiem 1,5 % (K-18).
D-4 kompensacja miejsc: kondygnacja −2 pod M1 (+6) Z KLATKĄ C PRZEDŁUŻONĄ DO −2 z przedsionkiem EI 30 (drugie wyjście z −2 pod skrzydłem, K-15 iii); przeprojektować przesłonę/podbicie przy Maz. 19 (S2-05) i warunek DGI (S2-01); bilans miejsc ≥ wymaganych wg v1.2b (107; cel ≥ 109 przy odczycie ostrożnym). MDS (v1.2b: 600 os. na −1, wyjście awaryjne = bliźniaczy szyb SZ-MDS + tunel 12,2 m poza ścianą szczelinową, poniżej ZWG, wycena 0,4455 mln): zweryfikuj wg L-02 technologię (szczelna obudowa tunelu i szybu do glin, uszczelnienie przejścia przez ścianę energetyczną, wypór, etapowanie) i realny koszt; jeśli inne rozwiązanie spełnia wymogi Dz.U. 2025 poz. 932 (§ 6–10) dla wyjść awaryjnych taniej i pewniej (np. wyjście w obrębie białej wanny z włazem poza strefą zagruzowania, klatka C do −2), zastosuj je; w przeciwnym razie zostaw szyb z poprawioną technologią i kosztem.
D-5 sala Sejmiku: ruszt dachu pn.–pd. ≤ 17,25 m, ściana pd. jako tarcza z cięgnem (~2,4 MN) na trzonie A i nowym słupie 0,60 × 0,60 m w filarze wsch. ciągłym do −2, ściana zach. nienośna; przejścia kanałów EIS przez tarczę tylko w środkowej tercji (K-9).
KOSZT: twardy limit 150 mln zł netto (R-222: wycena realna, bez zaniżania). Rezerwa może spaść z 5 % do 4 % (E-K-1 dopuszcza ≥ 4 %); szukaj dźwigni o najmniejszym wpływie na jakość architektury i bez naruszania wymogów obligatoryjnych (PV ≥ 400 kWp M.12, program, dostępność): filary pd. wieży w ceramice (−0,23), K-15 iii zamiast R2 (−0,27), oddymianie zamiast tryskaczy (już D-2), optymalizacje bez zmiany obrazu (np. zakres wykończeń zaplecza, systemy). Każda dźwignia z uzasadnieniem i wpływem.
DODATKOWE WYMAGANIA (z kontroli części opisowej i rejestru wymagań): (i) R-040 jest OBLIGATORYJNE-merytoryczne: miejsca oczekiwania na ewakuację dla osób na wózkach NA KLATKACH SCHODOWYCH w poziomie podestów kondygnacyjnych, niezawężające drogi ewakuacyjnej, z miejscem na krzesło ewakuacyjne i interkomem z ochroną i KDR – usuń „świadome odstępstwo” (miejsca w przedsionkach) i zaprojektuj poszerzone podesty we wszystkich klatkach (A, B, C, ew. A') na każdej kondygnacji, z kontrolą geometrii (pole wózka 0,90 × 1,40 m poza szerokością biegu/drogi, szerokość między poręczami wg decyzji v1.2b); (ii) R-036 (OBLIGATORYJNE): wszystkie wejścia do budynku bezpośrednio z poziomu chodnika, bez schodów i podjazdów – sprawdź każde wejście 1–8 i wejście do M1 na rzędnych NMT; (iii) oddymianie dróg poziomych / korytarzy kondygnacji biurowych deklarowane w opisie (§ 247 WT) nie jest wycenione – wycenić w koszcie albo zmienić koncepcję ppoż. spójnie (opis zostanie poprawiony później); (iv) F.15.C: PU 8850,37 vs spec 8868,23 i ogródki zachowane = 0 (generator bierze dane awaryjne) – napraw w tools/tabele_konkursowe.py, aby F.15.C brała dane z koncepcja.json v1.3 (budynek.json zostanie przeliczony później); (v) meta.wersja w koncepcja.json ustaw na „1.3 (audyt)”.
ZASADY: każda zmiana z dowodem w skrypcie (testy z assertami), wpis w koncepcja.json i md, pozycja w rejestrze (nowa sekcja „v1.3 – wdrożenie audytu” z ID audytu). Wymagania dla przebiegu rzutów (agent_rzutow: S3-ppoz-01, F2-program-biura-01, F1-komunikacja-01, -03, F2-program-biura-02, -04, -05, -07, -08, -10, S2-posadowienie-07 oraz testy z rozdz. 5.2 faza 2) zapisz jednoznacznie w koncepcja.json (np. klucz wymagania_rzutow_v13 z geometrią i testami) i w rejestrze – rzutów NIE generujesz.
WŁASNOŚĆ PLIKÓW: wolno: model/koncepcja.json (przez łańcuch skryptów + nowy idempotentny docs/20_koncepcja/_v13_audyt.py uruchamiany po _v12b_decyzje), docs/20_koncepcja/*.md, *.json, _v1*.py, _s2_*.py, _rewizja_parking.py, _rewizja_koszt_wejscie_v1_*.json, tools/tabele_konkursowe.py (tylko jeśli konieczne) i build/tabele/. NIE wolno: model/budynek.json, tools/model_pomieszczen.py, tools/rzuty.py, tools/elewacje.py i inne generatory rysunków, docs/95_opis/, src/umwd/render/, render/ (zmiany elewacji i geometrii zewnętrznej zgłoś precyzyjnie w open_items – agent 3D i generatory rysunków je wdrożą).`

const PART_A = `${CTX}
CZĘŚĆ A (wykonujesz jako pierwszy): GARAŻ, SEGMENT, TECHNIKA, WODA, MDS. Wdroż: D-1, D-2, D-4 oraz F3-garaz-technika-01…-10, S3-ppoz-04, S3-ppoz-07 (szachty, SZ-1), S3-ppoz-08 (zbiornik/pompownia ppoż., hydranty, nasada 75 mm), S3-ppoz-09 (trafo, SZR), S2-posadowienie-07 (przepompownia, separator, przelew), S1-konstrukcja-06 (segment), konflikty K-6, K-7 (BESS ≤ 60 kWh na kond. 1 albo na parterze), K-8, K-11, K-12, K-15, K-16, K-17; luki L-01 (ustal miarodajną rzędną wody powodziowej z dokumentów M.05/ISOK/MPZP i zapewnij, że wszystkie otwory podziemia i parteru są powyżej albo mają zamknięcia – zapisz listę otworów z rzędnymi i środkami), L-02 (usunięcie tunelu – zastąpione klatką C do −2), L-09 (dry-cooler/agregat: przepływ, recyrkulacja, hałas nocny vs okna WS 5 i Maz. 19, drgania). Przelicz garaż skryptem _rewizja_parking.py (geometria ramp, zatoka do zawracania, słupy ≤ 0,40 m w kierunku u, OzN na −2, EV tylko na stanowiskach niezależnych, R1 ≥ 3,50 m) i bilans miejsc (cel ≥ 106, zalecane ≥ 108). Uruchom łańcuch; walidacje muszą przejść. Zwróć raport: zmiany per ID audytu, liczby (miejsca, GPC, strefa garażu < 5 000 m²), open_items.`
const PART_B = (prevA) => `${CTX}
CZĘŚĆ A (garaż/segment/technika) została właśnie wdrożona przez innego autora; jego raport:
${String(prevA).slice(0, 7000)}
CZĘŚĆ B (Twoja): PARTER, HALA, KONFERENCJE, M1, KONSTRUKCJA NADZIEMNA, ELEWACJE. Wdroż: D-3, D-5 oraz S3-ppoz-02 (A jedyna przez Halę z drzwiami EI 30; B korytarz EI 60 1,6 m do lica pd.; C drzwi z podestu na dziedziniec), S3-ppoz-03 / F1-komunikacja-02 / F2-program-biura-01 część specyfikacyjna (pakiet G1), F1-komunikacja-10, S1-konstrukcja-08, S1-konstrukcja-03 (usunięcie pierścienia R 7,0, słupa (32,40; 23,15) i słupa łuku 45°; belka w nadprożu), S1-konstrukcja-01 (w kondygnacja_S2 i _s2_*.py), S1-konstrukcja-04, S3-ppoz-10, F1-komunikacja-01 (oś Hali wg K-5: pas ≥ 2,0 m wolny od przeszkód na całej długości, test ±1,0 m, ±3 m wolny od pomieszczeń na pierwszych 6 m od obu drzwi; drzwi ogrodowe w osi; PHS.04 usunięte, WC konferencyjne wg F2-02 i K-1…K-3; SW.06 i PHS.02 wg K-1/K-4; Hala jako hol klatki A z drzwiami EI 30 do każdego połączenia – K-14; kancelaria – wariant bezpieczny), F2-program-biura-02, -03 (słupki okienne w osi ścianek), -04 (strefa wzmocniona stropu), -05, F1-komunikacja-05, -07 (matryca stref), F2-program-biura-09, F3-garaz-technika-07, konflikty K-1…K-5, K-9, K-10, K-13, K-14, K-18; luki L-05 (akustyka sali: usuń ognisko łuku – np. pochylenie/segmentacja szkła lub ustroje rozpraszające – i policz RT 0,7–0,9 s z chłonnością; ściana mobilna sali 200 Rw), L-07 (oddziaływania wyjątkowe: uderzenie pojazdu w filary podcienia, słupki zabezpieczające, cięgno tarczy – redundancja), L-10 (dzień sesji: ewakuacja OzN z galerii i płyty – dźwig ewakuacyjny/strefa oczekiwania, stanowisko KDR, kontrola gości i mediów). Jeśli rozwiązanie K-5 koliduje z decyzją v1.2b o osi Hali, obowiązuje audyt (K-5) – zaktualizuj v1.2b. Uruchom łańcuch; walidacje muszą przejść. Zwróć raport per ID audytu + zmiany zewnętrzne (dla agenta 3D i elewacji) + open_items.`
const PART_C = (prevA, prevB) => `${CTX}
Części A i B zostały wdrożone. Raporty:
A: ${String(prevA).slice(0, 4500)}
B: ${String(prevB).slice(0, 6000)}
CZĘŚĆ C (Twoja): POSADOWIENIE, TECHNOLOGIA, ETAPOWANIE, KOSZT, DOMKNIĘCIE. Wdroż: S2-posadowienie-01 (III kategoria geotechniczna, DGI, warunek ≥ 2 m w ciągłą QpB), S2-posadowienie-05 (przesłona przy Maz. 19 – zgodnie z D-4), F3-garaz-technika-08 (technologia sond GPC), luki L-03 (koncepcja etapowania realizacji wymagana umową F.01 – wykonalny podział z zabezpieczeniem wyporu i wyjściami MDS w każdym etapie), L-04 (technologia budowy podziemia: metoda stropowa vs rozparcie, pale/słupy wstępne/barety z kosztem, przeszkody w nasypach, zaplecze budowy w fazach), L-06 (drgania i hałas od planowanego tramwaju w Mazowieckiej – izolacja sali obrad i stref pracy, zgodność z MPZP bez ekranów), L-08 (rezerwy w szachtach i trasach ≥ 15–20 %, R-044). Następnie KOSZT: zbierz wszystkie delty z A, B, C w _v13_koszt.py (kontrakt f14b_rows jak _v12_koszt.py; find_revision w tabele_konkursowe.py musi wybrać najnowszy), wybierz dźwignie (zasady w KONTEKŚCIE), wynik ≤ 150 mln netto z rezerwą ≥ 4 % i zapasem ≥ 0,3 mln – raportuj uczciwie, bez zaniżania. Uruchom cały łańcuch + tools/tabele_konkursowe.py (F.14.B, F.15.A–C). Na koniec TABELA ZAMKNIĘCIA AUDYTU: dla każdego z 41 ID i L-01…L-10: status (wdrożone w spec / przekazane do rzutów z wymaganiem / uzasadnione odstąpienie) + gdzie. Zwróć: tabela zamknięcia, key_numbers (koszt, rezerwa, zapas, PU, PC, miejsca, MDS), changed_files, open_items (dla rzutów, 3D, rysunków, opisu).`

phase('Revise')
const A = await agent(PART_A, { label: 'revise:A-garaz-segment', phase: 'Revise' })
const B = await agent(PART_B(A), { label: 'revise:B-parter-konstrukcja', phase: 'Revise' })
const C = await agent(PART_C(A, B), { label: 'revise:C-grunt-koszt-domkniecie', phase: 'Revise' })

const PROB = {
  type: 'object',
  properties: {
    problems: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['KRYTYCZNY', 'ISTOTNY', 'DROBNY'] },
      audit_id: { type: 'string' }, where: { type: 'string' }, problem: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } },
      required: ['severity', 'audit_id', 'where', 'problem', 'evidence', 'fix'] } },
    unclosed_audit_ids: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['problems', 'unclosed_audit_ids', 'summary'],
}
const LENSES = [
  ['ppoz-ewakuacja', 'OCHRONA PRZECIWPOŻAROWA I EWAKUACJA: sprawdź na geometrii z koncepcja.json (policz w shapely) każdą drogę ewakuacyjną parteru, −1, −2 (z −2 pod M1 i klatką C), S/ANT i kondygnacji biurowych: przedsionki, wyjścia z sal > 50 os. (2 wyjścia ≥ 5 m), dojścia i przejścia (WT § 237, § 242, § 256, § 278 z samoczynnym oddymianiem), Hala jako hol klatki A (§ 256 ust. 6, drzwi EI 30), strefy pożarowe (garaż < 5 000 m²), zbiornik/pompownia ppoż., hydranty, szachty wentylacji pożarowej, oddzielenie od Maz. 19 (S3-10), ewakuacja OzN z galerii (L-10).'],
  ['konstrukcja-grunt-woda', 'KONSTRUKCJA, POSADOWIENIE, WODA: drogi obciążeń (tarcza sali, cięgno, nowy słup do −2, usunięte słupy i przęsło podcienia 6,99 m, belki krawędziowe przy bramie 6,0 m, segment), wypór i etapowanie (L-03), technologia (L-04), −2 pod M1 przy Maz. 19 (podbicie, przesłona, DGI), rzędne wody powodziowej i otwory (L-01), sondy GPC (F3-08), oddziaływania wyjątkowe (L-07). Licz orientacyjnie (L/h, siły, wypór).'],
  ['funkcja-parking-koszt', 'FUNKCJA, GARAŻ, KOSZT, SPÓJNOŚĆ: geometria ramp (5,5/6,0 m, łuki, nachylenia, skrajnie), zatoka do zawracania, liczba miejsc ≥ 106 (przelicz _rewizja_parking.py sam), OzN i EV, dostawy i odpady (F3-05), droga wewnętrzna z dz. 10/2 (F3-06), pakiet G1 i oś Hali (K-5 – policz pas), WC konferencyjne, matryca stref; koszt: czy wszystkie delty wycenione realnie, dźwignie uzasadnione, ≤ 150 mln z rezerwą ≥ 4 %; czy JSON, md, rejestr i F.14.B/F.15 są zgodne; czy wymagania dla rzutów (wymagania_rzutow_v13) są kompletne i jednoznaczne.'],
]
phase('Verify')
const ver = await parallel(LENSES.map(([k, p]) => () => agent(`${CTX}
Jesteś NIEZALEŻNYM WERYFIKATOREM (soczewka: ${k}) rewizji v1.3. Raport domknięcia autora:
${String(C).slice(0, 9000)}
${p}
Dodatkowo: dla każdego ID audytu z Twojej soczewki sprawdź, czy jest naprawdę zamknięty (nie tylko deklaratywnie) – wpisz niezamknięte do unclosed_audit_ids. Raportuj tylko problemy, które udowodnisz (plik:miejsce, obliczenie). Nie edytuj plików.`, { label: `verify:${k}`, phase: 'Verify', schema: PROB })))
const probs = ver.filter(Boolean).flatMap(v => v.problems)
const unclosed = [...new Set(ver.filter(Boolean).flatMap(v => v.unclosed_audit_ids))]
log(`verify: ${probs.length} problems (${probs.filter(p => p.severity === 'KRYTYCZNY').length} critical), unclosed: ${unclosed.join(', ')}`)

phase('Fix')
const fix = (probs.length === 0 && unclosed.length === 0) ? 'no problems' : await agent(`${CTX}
Jesteś autorem rewizji v1.3 (poprawki po weryfikacji). Raport domknięcia:
${String(C).slice(0, 6000)}
Weryfikatorzy zgłosili problemy (JSON):
${JSON.stringify(probs, null, 1)}
Niezamknięte ID audytu wg weryfikatorów: ${unclosed.join(', ')}
Każdy problem sprawdź sam; popraw, jeśli zasadny, albo odrzuć z konkretnym uzasadnieniem. Uruchom ponownie cały łańcuch i tabele; walidacje muszą przejść. Zaktualizuj tabelę zamknięcia audytu w rejestrze. Zwróć: problem → poprawiony/odrzucony (+powód), końcowa tabela zamknięcia (skrót), key_numbers, changed_files, open_items (rzuty, 3D, rysunki, opis).`, { label: 'fix', phase: 'Fix' })

return { A, B, C, problems: probs, unclosed, fix }
