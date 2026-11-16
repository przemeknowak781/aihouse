# Bezpieczeństwo pożarowe – wymagania i dobre praktyki dla koncepcji (UMWD Wrocław)

| | |
|---|---|
| Stan prawny na dzień | **16.11.2026** (sprawdzony w API ELI Sejmu/ISAP; <!-- poprawione przez weryfikatora --> ostatnia pozycja Dz.U. w bazie ELI przy weryfikacji: 2026 poz. 1497 z 13.11.2026; weryfikacja adwersaryjna ok. 45 twierdzeń – 16.11.2026, rozdz. 19) |
| Obiekt | budynek administracyjny UMWD: biura (ZL III), sala obrad Sejmiku i sale konferencyjne (ZL I), 2 kondygnacje podziemne (garaż PM, technika), dominanta 35–45 m (MPZP), skrzydła ≤ 25 m, przyleganie do Mazowiecka 19 |
| Kategoria wysokości | **wysoki (W)** – 25 m < H ≤ 55 m (§ 8 pkt 3 WT) |
| Status dokumentu | opracowanie robocze dla koncepcji konkursowej; nie zastępuje uzgodnienia z rzeczoznawcą ds. zabezpieczeń ppoż. |
| Zakaz | nie korzystano z żadnych informacji o pracach nagrodzonych/konkurencyjnych w tym konkursie (nie wyszukiwano ich, nie napotkano) |

Oznaczenia: **[O]** – przepis obowiązujący; **[P]** – przepis, który utracił moc, ale wolno go stosować przejściowo (art. 102a Pb); **[PR]** – projekt aktu (nieobowiązujący); **wniosek** – wniosek własny autora; *źródło wtórne* – portal branżowy (pomocniczo). Numery źródeł [S…] – lista w rozdz. 18.

---

## 1. Najważniejsze wnioski (TL;DR)

1. **Luka w warunkach technicznych.** Rozporządzenie MI z 12.04.2002 w sprawie warunków technicznych (WT 2002) **utraciło moc z upływem 19.09.2026** (ISAP: „uznany za uchylony”, podstawa: art. 66 ustawy o zapewnianiu dostępności) [S1]. <!-- poprawione przez weryfikatora --> *Uwaga weryfikatora:* art. 66 ustawy o dostępności (w/ż 20.09.2019) daje „nie dłużej niż 84 miesiące”; ISAP/ELI podaje datę uchylenia **21.09.2026** (co wg konwencji bazy oznacza ostatni dzień mocy 20.09.2026), natomiast ustawodawca w art. 102a Pb pisze o przepisach „obowiązujących do dnia 19 września 2026 r.” – rozbieżność jednodniowa bez znaczenia praktycznego dla koncepcji (rozstrzyga art. 102a). **Nowe WT nie zostały ogłoszone** (brak w Dz.U. do 16.11.2026 – wyszukiwanie ELI) [S1][S15]. Ustawa z 31.07.2026 (Dz.U. 2026 poz. 1161) dodała do Prawa budowlanego **art. 102a**: przez **18 miesięcy od 20.09.2026 (do 20.03.2028)** projekt może być sporządzony wg WT 2002 po złożeniu **oświadczenia inwestora** [S6]. → **Wniosek:** koncepcję projektujemy wg WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.), ale tak, by **spełniała też projekt nowych WT (wersja 24.04.2026)** tam, gdzie to tanie (MOE, elewacje A2-s1,d0, dźwig ewakuacyjny). Wniosek o PnB tej inwestycji najpewniej wpłynie po 20.03.2028.
2. **Klasa odporności pożarowej „B”** dla całego budynku (ZL I i ZL III w W) [§ 212 ust. 2 WT]; tryskacze **nie** pozwalają obniżyć klasy w budynku W (§ 214).
3. **Strefa pożarowa ZL ≤ 2500 m²** w budynku W – **bez możliwości powiększenia** tryskaczami/oddymianiem (§ 227 ust. 1 i 4). Każda kondygnacja może być odrębną strefą (§ 226 ust. 2). Antresole, pustki i atria **sumują** powierzchnie połączonych kondygnacji.
4. **Min. 2 klatki schodowe obudowane, z przedsionkami przeciwpożarowymi** i **urządzeniami zapobiegającymi zadymieniu** (nadciśnienie) w klatkach i przedsionkach (§ 246 ust. 1–2). Przedsionki ≥ 1,4 × 1,4 m (§ 232 ust. 3) – dla OzN i krzesła ewakuacyjnego praktycznie ≥ ok. 2,0 × 2,4 m (wniosek).
5. **Poziome drogi ewakuacyjne muszą być zabezpieczone przed zadymieniem** (§ 247 ust. 1) – oddymianie korytarzy/holi → szachty, klapy, wentylatory na dachu: zarezerwować miejsce już w koncepcji.
6. **Dźwig dla ekip ratowniczych obowiązkowy** (posadzka najwyższej kondygnacji > 25 m; § 253) – przez przedsionek ppoż., szyb REI 60, nadciśnienie, PN-EN 81-72; dojście od drogi pożarowej ≤ 50 m łącznie z drogą w budynku (§ 12 ust. 5 rozp. 2009).
7. **SSP i DSO obowiązkowe** (budynek użyteczności publicznej wysoki; § 28 ust. 1 pkt 10 i § 29 ust. 1 pkt 5 rozp. 2010). **Hydranty 25** na każdej kondygnacji, **zawory 52** na pionach DN 80 (2 szt./pion na kondygnacjach > 25 m i podziemnych), zbiornik ppoż. 100 m³ lub redukcja do 50/25 m³ przy zasilaniu z sieci (rozp. 2010 § 19–25). **Tryskacze nie są obowiązkowe** dla W biurowego, ani dla garażu 2-kondygnacyjnego – rekomendujemy je jednak w całym budynku (wniosek, rozdz. 7.3).
8. **Długości dojść:** ZL III – 30 m (w tym ≤ 20 m poziomo) / 60 m; ZL I (piętra Sejmiku, sale konferencyjne) – **10 m / 40 m**; +50% za tryskacze, +50% za oddymianie drogi, łącznie +100% (§ 256 ust. 3–4). Mierzone do pierwszych drzwi przedsionka.
9. **Elewacja powyżej 25 m – okładzina, mocowania i izolacja niepalne** (§ 216 ust. 8); cała ściana zewnętrzna NRO; **pasy międzykondygnacyjne 0,8 m EI 60** lub równoważne (§ 223); mocowania nieodpadające ≥ 60 min (§ 225). Projekt nowych WT zaostrza to do **A1 lub A2,d0** → przyjąć **A1/A2-s1,d0** (wniosek).
10. **Sąsiedzi:** przy Mazowiecka 19 – **ściana oddzielenia przeciwpożarowego REI 120** bez otworów (§ 272 ust. 3, § 232 ust. 4) + pas elewacyjny 2 m EI 60 lub wysunięcie 0,3 m (§ 235 ust. 2) + **brak okien nad dachem MZ19** w pasie 8 m do wys. 10 m (<!-- poprawione przez weryfikatora --> wniosek z § 218: przepis stawia wymagania **dachowi budynku niższego** – NRO, konstrukcja R 30, przekrycie RE 30 w pasie 8 m od ściany z otworami budynku wyższego – chyba że najbliższy otwór jest ≥ 10 m nad tym dachem i Q ≤ 2000 MJ/m²; ponieważ dachu MZ19 nie przebudujemy, rozwiązaniem jest brak otworów w naszej ścianie do 10 m nad jej dachem). Od ściany szczytowej z oknami **Wybrzeże Słowackiego 5**: odległość **8 m** (gdy nasza ściana ma > 65% powierzchni „pełnej” E), **12 m / 16 m** przy większym przeszkleniu, –25% przy tryskaczach w naszym budynku (§ 271).
11. **Drogi pożarowe**: wymagane (ZL I; W z ZL III); przy zabudowie pierzejowej – wzdłuż **100% elewacji frontowej**, krawędź **5–15 m** od ściany, szer. 4 m, spadek ≤ 5%, nacisk osi 100 kN, **bez drzew > 3 m** między drogą a elewacją (rozp. 2009 § 12–13). Zieleń skweru od Wybrzeża Słowackiego musi to uwzględnić.
12. **Garaż (PM, 2 kondygnacje podziemne):** strefa ≤ 5000 m² (+100% z tryskaczami), oddymianie gdy > 1500 m² lub brak bezpośredniego wyjazdu, SSP (gdy > 1500 m² lub > 1 kondygnacja podziemna), hydranty 33, przedsionki EI 30 do budynku, przejście do wyjścia ≤ 40 m (§ 277–280 WT; § 28 ust. 1 pkt 17 rozp. 2010).
13. **Interfejs obrony cywilnej (poza ppoż., ale krytyczny):** od 29.05.2026 w budynku użyteczności publicznej **„zapewnia się budowlę ochronną”** (art. 93 ustawy o ochronie ludności, Dz.U. 2026 poz. 646), a nasz budynek **nie mieści się w zwolnieniach ustawowych** z rozp. Dz.U. 2026 poz. 1181 § 2. Program zakłada jedynie MDS w garażu – **ryzyko do przeanalizowania przez zespół prawny** (rozdz. 13).
14. **Miejsca oczekiwania na ewakuację (MOE)** na podestach klatek (wymóg Regulaminu) – projektować poza wymaganą szerokością biegu/spocznika, z miejscem na krzesło ewakuacyjne i interkomem (EVCS) do ochrony i stanowiska KDR; spójnie z projektem nowych WT § 252 [PR].

---

## 2. Stan prawny na 16.11.2026

### 2.1. Warunki techniczne – co dokładnie obowiązuje

| Akt | Publikator | Status 16.11.2026 | Uwagi | Źródło |
|---|---|---|---|---|
| Rozp. MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (WT 2002) | t.j. Dz.U. 2022 poz. 1225; zm. Dz.U. 2023 poz. 2442 (<!-- poprawione przez weryfikatora --> **w/ż 1.08.2024** – pierwotny termin 1.04.2024 przesunięty przez § 1 pkt 2 rozp. Dz.U. 2024 poz. 474), 2024 poz. 474 (w/ż 1.04.2024), 2024 poz. 726 (w/ż 15.08.2024) | **[P] utraciło moc z upływem 19.09.2026**; ISAP: „uznany za uchylony”, uchylenie wynikające z ustawy Dz.U. 2019 poz. 1696 (art. 66), data w bazie 2026-09-21 | Zmiany 2023–2024 w dziale VI (ppoż.) dotyczą wyłącznie budynków niskich (<!-- poprawione przez weryfikatora --> oraz – § 216 ust. 2 pkt 5 – dachów hal sportowych/basenów SW; drewno klejone/lite, § 216 ust. 2 pkt 4–5, § 232 ust. 8–9, § 249 ust. 5a); rozp. 2023 poz. 2442 nie zmienia działu VI – **nie zmieniają wymagań dla budynku W** | [S1][S2][S3][S4][S5] |
| Prawo budowlane – art. 102a–102c (rozdz. 10a „Przepisy epizodyczne”) | dodane ustawą z 31.07.2026, Dz.U. 2026 poz. 1161 (art. 2 pkt 4 w/ż **2.09.2026** – dzień po ogłoszeniu 1.09.2026, art. 5; reszta ustawy w/ż 2.10.2026) | **[O]** | Przez 18 mies. od 20.09.2026 PZT/PAB (do wniosku o PnB, zatwierdzenie projektu, zgłoszenie) mogą być sporządzone wg przepisów z art. 7 ust. 2 pkt 1 obowiązujących do 19.09.2026, **po złożeniu oświadczenia inwestora**; wtedy także PT wg tych przepisów (ust. 2), a decyzje dla całego zamierzenia wg tych przepisów (ust. 4) | [S6] |
| Prawo budowlane | t.j. Dz.U. 2026 poz. 524, zm. poz. 605, 646, 1161, 1347 | [O] | art. 5 ust. 1 pkt 1 lit. b (bezpieczeństwo pożarowe – wymaganie podstawowe), art. 7 ust. 2 pkt 1 (delegacja WT), art. 9 (odstępstwo), art. 29 ust. 4 pkt 3 lit. c (PV > 6,5 kW – uzgodnienie z rzeczoznawcą) | [S7] |
| Projekt rozp. **Ministra Finansów i Gospodarki** w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie oraz warunków technicznych użytkowania budynków mieszkalnych (nowe WT) | projekt z 24.04.2026 (udostępniony w uzgodnieniach z KWRiST); OSR z 11.05.2026; nr projektu RCL wg źródła wtórnego: 12398903 | **[PR] nieogłoszony** | Planowane w/ż 20.09.2026 (§ 393 projektu) – **nie nastąpiło**. *Źródło wtórne* [W2] wskazuje nowszą wersję z 6.08.2026 na etapie notyfikacji UE – **niezweryfikowane** (RCL i TRIS niedostępne 16.11.2026: HTTP 503/401) | [S15][W1][W2] |

**Wniosek – strategia prawna dla koncepcji:**
- Harmonogram realizacyjny (konkurs 2026 → umowa → projekt budowlany) sprawia, że wniosek o PnB prawdopodobnie zostanie złożony **po 20.03.2028**, tj. po upływie okna z art. 102a. Wtedy zastosowanie będą miały **nowe WT** (o ile zostaną wydane) – a ich ostateczna treść jest nieznana.
- Dlatego w koncepcji: (a) spełniamy **WT 2002** (bo tylko one mają dziś postać aktu i są przywołane przez Organizatora – np. odp. na pyt. 78 w Wyjaśnieniach nr 20 powołuje „t.j. Dz.U. z 2022 r. poz. 1225 ze zm.”); (b) „uzbrajamy” projekt w rozwiązania wymagane przez **projekt nowych WT** tam, gdzie koszt jest mały (tabela 2.3); (c) w opisie konkursowym piszemy neutralnie: „zgodnie z przepisami techniczno-budowlanymi obowiązującymi na dzień złożenia wniosku o PnB; koncepcja spełnia wymagania WT 2002 i projektu nowych WT (wersja 24.04.2026)”.
- <!-- poprawione przez weryfikatora --> Rozp. MSWiA 2009 (§ 2 ust. 1 – definicje budynków, kategorii ZL, stref, kondygnacji, grup wysokości) odsyła do konkretnego aktu: „Dz. U. Nr 75, poz. 690, z późn. zm.”, a rozp. MSWiA 2010 (§ 2 pkt 5) – do WT w t.j. Dz.U. 2022 poz. 1225 („przepisy techniczno-budowlane”). Odesłania wskazują konkretny akt, ale wobec jego utraty mocy ich wykładnia jest **niepewna** (sporne, czy stosować treść WT 2002 jako definicyjną, czy przyszłe nowe WT). Wniosek: do czasu nowych WT przyjmować definicje WT 2002 (spójne z art. 102a Pb); kwestia do potwierdzenia z rzeczoznawcą ppoż.

### 2.2. Przepisy przeciwpożarowe „resortowe” (MSWiA) i ustawowe

| Akt | Publikator | Status | Najważniejsze dla nas | Źródło |
|---|---|---|---|---|
| Ustawa z 24.08.1991 o ochronie przeciwpożarowej | t.j. Dz.U. 2025 poz. 188, zm. Dz.U. 2026 poz. 815 (w/ż 4.07.2026) | [O] | art. 6a (rozwiązania zamienne – zgoda KW PSP), art. 6b (uzgodnienie projektu z rzeczoznawcą), art. 6c–6f | [S9] |
| Rozp. MSWiA z 7.06.2010 w sprawie ochrony przeciwpożarowej budynków, innych obiektów budowlanych i terenów | t.j. Dz.U. 2023 poz. 822; zm. Dz.U. 2024 poz. 1716 (w/ż 23.12.2024), Dz.U. 2026 poz. 1276 (w/ż **30.09.2026**) | [O] | § 15 (warunki ewakuacji), § 19–26 (instalacja wodociągowa ppoż.), § 27 (SUG), § 28 (SSP), § 29 (DSO); zm. 2024 (<!-- poprawione przez weryfikatora -->§ 4 ust. 2 pkt 6): oznakowanie styku ściany oddzielenia z elewacją/dachem w budynkach **handlowych, produkcyjnych i magazynowych** ze strefami ≥ 2000 m² każda (przy palnych ścianach/dachu lub Q > 1000 MJ/m²) – nas nie dotyczy; § 28a – autonomiczne czujki dymu/CO w lokalach mieszkalnych i hotelowych; zm. 2026: **oznakowanie punktów schronienia** (§ 4 ust. 2 pkt 7, zał. 1a) | [S10][S11][S12] |
| Rozp. MSWiA z 24.07.2009 w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych | Dz.U. 2009 nr 124 poz. 1030 | [O] (brak zmian i t.j.; nowego aktu brak) | § 3–5, 10 (woda zewnętrzna, hydranty), § 12–15 (drogi pożarowe, place manewrowe, przejazdy) | [S13] |
| Rozp. MSWiA z 5.08.2023 w sprawie uzgadniania projektu … pod względem zgodności z wymaganiami ochrony przeciwpożarowej | Dz.U. 2023 poz. 1563 (w/ż 9.08.2023; zastąpiło Dz.U. 2021 poz. 1722) | [O] | § 3 ust. 1 pkt 1, 2, 6 – nasz budynek i garaż **wymagają uzgodnienia** z rzeczoznawcą | [S14] |
| Ustawa z 19.07.2019 o zapewnianiu dostępności osobom ze szczególnymi potrzebami | t.j. Dz.U. 2024 poz. 1411 ze zm. | [O] | **art. 6 pkt 1 lit. e** – zapewnienie osobom ze szczególnymi potrzebami możliwości ewakuacji lub ich uratowania w inny sposób | [S8] |
| Ustawa z 5.12.2024 o ochronie ludności i obronie cywilnej + akty wykonawcze | Dz.U. 2024 poz. 1907; zm. 2025 poz. 1705 (<!-- poprawione przez weryfikatora --> w/ż 1.01.2027 – jeszcze nieobowiązująca), **2026 poz. 646** (w/ż 29.05.2026), 2026 poz. 815 (w/ż 4.07.2026); rozp. Dz.U. 2025 poz. 932 (MDS), 2025 poz. 1548 (budowle ochronne), **2026 poz. 1181** (zwolnienia) | [O] | art. 93–95a (budowla ochronna w budynku użyteczności publicznej / MDS) – patrz rozdz. 13 | [S16][S17][S18][S19] |

### 2.3. Różnice WT 2002 ↔ projekt nowych WT (24.04.2026) istotne dla tej koncepcji

| Temat | WT 2002 [P] | Projekt WT [PR] | Decyzja koncepcyjna (wniosek) |
|---|---|---|---|
| Grupy wysokości | N ≤ 12 m, SW ≤ 25 m, W ≤ 55 m, WW > 55 m (§ 8) | identyczne (§ 8 ust. 1); kondygnacja nadziemna liczona od „poziomu przylegającego terenu” (§ 8 ust. 2) | bez zmian – budynek **W** |
| Strefa ZL w W | 2500 m², bez powiększeń (§ 227) | 2500 m², bez powiększeń (§ 239) | bez zmian |
| Elewacja > 25 m | izolacja, okładzina, mocowania **niepalne** (A1; A2 – dowolne s, d) (§ 216 ust. 8) | **A1 lub A2,d0**; dopuszczone wyjątki: uszczelki, masy, folie w szybach laminowanych, łączniki tworzywowe z trzpieniem stalowym – jeśli elewacja pozostaje NRO (§ 227 ust. 9–10) | przyjąć **A1 / A2-s1,d0** dla całej elewacji wentylowanej (wełna mineralna, okładziny ceramiczne/kamienne/metalowe) |
| Pas międzykondygnacyjny | 0,8 m (lub równoważne 0,5 m wysięgu / suma 0,8 m); 1,2 m nad PM > 1000 MJ/m² (§ 223–224) | jw.; **także w ścianach przekrytego dziedzińca (atrium)**; **zwolnienie w budynku z tryskaczami**; pas przy stropie oddzielenia z A1/A2,d0 (§ 234–236) | zaprojektować pasy 0,8 m EI 60 niezależnie od tryskaczy (odporność na oba reżimy) |
| Miejsca oczekiwania na ewakuację OzN | brak przepisu (tylko ogólne § 207 ust. 1 pkt 4 + art. 6 pkt 1 lit. e ustawy o dostępności) | szczegółowo (§ 247 ust. 3, § 252, § 258): pomieszczenie ≥ 1,5 × 3 m EI 60/S200 albo punkty w klatce schodowej (zał. 11), oświetlenie ≥ 5 lx, **EVCS** (łączność dwukierunkowa), dojście ≤ 20 m (ZL I: ≤ dł. dojścia przy 1 kierunku), dostęp ratowników ≤ 10 m od klatki/przedsionka dźwigu ratowniczego | punkty MOE na podestach + EVCS (wymóg Regulaminu i tak to narzuca) |
| Dźwig ewakuacyjny OzN | brak | dopuszczony wg PN dot. ewakuacji OzN dźwigami (PN-EN 81-76), szyb REI 60, nadciśnienie, przedsionek z punktami 1,5 × 0,9 m (§ 253) | min. 1 dźwig w trzonie wieży jako **ratowniczy (PN-EN 81-72) + ewakuacyjny (PN-EN 81-76)** |
| Jedna klatka w W | dopuszczalna, gdy kondygnacja ≤ 750 m² i brak ZL II (§ 246 ust. 4) | dodatkowo wymagany dźwig dla ekip ratowniczych (§ 260 ust. 4) | **nie korzystać** – zawsze 2 klatki |
| Pomiar dojścia do przedsionka | do pierwszych drzwi przedsionka (§ 256 ust. 1) | tylko gdy droga w przedsionku do drzwi klatki ≤ 5 m (§ 268 ust. 3) | przedsionki zwarte (≤ 5 m drogi) |
| Ewakuacja przez hol | warunki § 256 ust. 6 | + hol oddzielony od klatki jak klatka, od przyległych pomieszczeń jak droga ogólna (§ 268 ust. 8) | jedna klatka przez hol główny, wydzielenie holu EI 30/dymoszczelne |
| Zabezpieczenie dróg poziomych przed zadymieniem (W) | zawsze poza ZL IV (§ 247 ust. 1) | zwolnienie m.in. dla ZL w 4 najniższych kondygnacjach, gdy wyższe piętra nie łączą się z nimi komunikacyjnie (poza dźwigiem ratowniczym) (§ 261 ust. 2 pkt 4) | projektować oddymianie wszystkich poziomych dróg w W |
| Odrębne budynki nad garażem | tylko ściana od fundamentu do dachu (§ 210) | dodatkowo: części nadziemne na stropie oddzielenia garażu z **tryskaczami** (§ 221 ust. 2) | opcja „skrzydła jako odrębne budynki SW” – rozdz. 4.4 |
| Garaż w budynku | strefa PM (§ 209 ust. 3) | wprost: odrębna strefa pożarowa (§ 287 ust. 1); doprecyzowane oddymianie ≤ 1500 m² (§ 289) | bez zmian koncepcyjnych |
| PV / magazyn energii (BESS) | brak przepisów szczególnych (poza art. 29 ust. 4 pkt 3 lit. c Pb) | PV: przewody DC na zewnątrz lub w osłonie EI 30/EI 60, **wyłącznik awaryjny PV** (§ 303–304); BESS > 2 kWh: ≤ 600 kWh na strefę, > 60 kWh tylko na I kondygnacji podziemnej/nadziemnej, > 300 kWh tylko na parterze z dostępem z zewnątrz, **zakaz powyżej 25 m** (wyjątki z SUG/na stropodachu REI 60) (§ 310–312) | magazyn energii **na parterze lub –1 z bezpośrednim dostępem z zewnątrz**, nie na piętrze technicznym w wieży |

---

## 3. Klasyfikacja pożarowa budynku

### 3.1. Wysokość i grupa wysokości [P]
- **§ 6 WT:** wysokość mierzy się od poziomu terenu przy najniżej położonym wejściu na I kondygnacji nadziemnej do górnej powierzchni najwyżej położonego stropu (z izolacją i warstwą osłaniającą), bez maszynowni dźwigów i innych pomieszczeń technicznych ponad tę płaszczyznę, albo do najwyższego punktu stropodachu nad pomieszczeniami na pobyt ludzi.
- **§ 8 pkt 3 WT:** wysoki (W) – ponad 25 m do 55 m włącznie.
- MPZP (§ 26 ust. 2 pkt 3, cytowany w odp. na pyt. 57, Wyjaśnienia nr 8): w obszarze A wymiar pionowy do najwyższego punktu pokrycia dachu ≤ 45 m, do najniższego ≥ 35 m. → **Wniosek:** wysokość wg § 6 WT ≈ 34–45 m → **W** w każdym wariancie; posadzka najwyższej kondygnacji (sala Sejmiku) > 25 m → obowiązek dźwigu ratowniczego (§ 253).
- **Pułapka (§ 212 ust. 5 WT):** jeżeli część podziemna jest zaliczona do **ZL** (np. pomieszczenia biurowe, socjalne, sale, MDS „na stałe” jako ZL), do ustalenia klasy odporności liczy się **sumę wysokości części podziemnej i nadziemnej** – chyba że część podziemna jest oddzielona elementami REI 120 i ma bezpośrednie wyjścia na zewnątrz. 45 m + 2 kondygnacje podziemne (~8 m) = 53 m (W), ale przy 3 kondygnacjach podziemnych > 55 m → klasa jak dla **WW = „A”**. **Wniosek:** w podziemiu tylko garaż (PM) i technika; pomieszczenia ZL w podziemiu – wydzielić REI 120 z bezpośrednim wyjściem na zewnątrz lub ich unikać.

### 3.2. Kategorie zagrożenia ludzi [P] (§ 209 WT)

| Część budynku | Kategoria | Uzasadnienie |
|---|---|---|
| Biura, sale narad 30-os., kancelaria, hol (bez zgromadzeń) | **ZL III** | budynek użyteczności publicznej (§ 3 pkt 6 – także biurowy), nie ZL I/II (§ 209 ust. 2 pkt 3) |
| Sala obrad Sejmiku (do 100 os. + publiczność, media, goście) | **ZL I** | pomieszczenie dla > 50 osób niebędących jego stałymi użytkownikami (§ 209 ust. 2 pkt 1) |
| Sala konferencyjna 200 os., sala 80 os., ew. sala komisji 50 os. | **ZL I** (sala 50-os. – na granicy: „ponad 50”; przy pow. > 50 m² i braku jednoznacznej aranżacji § 236 ust. 6 każe liczyć **1 m²/os.**) | jw. |
| Bistro / przestrzeń gastronomiczna (kilkanaście stolików) | ZL III (gdy ≤ 50 os.) | — |
| Garaż, hydrofornia, rozdzielnie, trafostacja, maszynownie, agregat, BESS | **PM** (§ 209 ust. 3) | — |

- **§ 209 ust. 5:** strefa zaliczona do kilku kategorii spełnia wymagania **każdej** z nich. **Wniosek:** jeżeli sala ZL I leży w tej samej strefie co biura, cała strefa musi spełniać ostrzejsze wymagania ZL I (dojścia 10/40 m). Najprościej: **kondygnacje Sejmiku i strefa konferencyjna jako odrębne strefy ZL I**, piętra biurowe jako strefy ZL III.
- **§ 236 ust. 6 – gęstości do obliczeń** (gdy liczba osób nie wynika jednoznacznie z programu): sale konferencyjne, hole, poczekalnie – **1 m²/os.**; pomieszczenia administracyjno-biurowe – **5 m²/os.**; archiwa – 7 m²/os.; magazyny – 30 m²/os.

### 3.3. Klasa odporności pożarowej i klasy elementów [P]
- **§ 212 ust. 2:** W – ZL I i ZL III → **„B”**. Część podziemna nie niższa niż „C” i nie niższa niż część nad nią (§ 212 ust. 7) → podziemie także „B” (wniosek). Garaż: klasa jak dla PM Q ≤ 500 MJ/m² (§ 275 ust. 1) → dla W również „B” (§ 212 ust. 4).
- **§ 214:** obniżenie klasy dzięki tryskaczom **nie dotyczy** wielokondygnacyjnych budynków W.
- **§ 216 ust. 1 – wymagania dla klasy „B”:**

| Element | Klasa |
|---|---|
| Główna konstrukcja nośna | **R 120** |
| Konstrukcja dachu | R 30 |
| Strop | **REI 60** |
| Ściana zewnętrzna (pas międzykondygnacyjny z połączeniem ze stropem) | **EI 60 (o↔i)** |
| Ściana wewnętrzna | EI 30 |
| Przekrycie dachu | RE 30 |

- **§ 216 ust. 2:** wszystkie te elementy **nierozprzestrzeniające ognia (NRO)**.
- **§ 212 ust. 9:** pomieszczenia zbiorników ppoż., pomp ppoż., maszynowni wentylacji pożarowej i rozdzielni zasilających urządzenia niezbędne podczas pożaru – **odrębne strefy pożarowe**.
- **§ 212 ust. 8:** pomieszczenia techniczne/magazynowe niepowiązane funkcjonalnie z ZL – odrębna strefa PM.

**Wniosek konstrukcyjny:** żelbet/stal zabezpieczona do R 120 – bez trudności; konstrukcja drewniana lub hybrydowa CLT w budynku W „B” jest w praktyce wykluczona bez rozwiązań zamiennych (art. 6a ustawy ppoż.) – nie proponować w konkursie jako głównego ustroju (dopuszczalne np. drewno w okładzinach wnętrz spełniających § 258–262 lub w elementach niekonstrukcyjnych ≤ 25 m, z ostrożnością).

---

## 4. Strefy pożarowe i oddzielenia

### 4.1. Wielkość stref [P]
- **§ 226 ust. 1–3:** strefa = budynek lub część oddzielona elementami oddzielenia ppoż. (§ 232 ust. 4) albo pasami wolnego terenu; częścią budynku jest też **kondygnacja**, jeżeli klatki schodowe i szyby dźwigowe spełniają co najmniej § 256 ust. 2 (obudowane, drzwi EI 30, urządzenia zapobiegające zadymieniu). Do powierzchni strefy wlicza się antresole.
- **§ 227 ust. 1:** ZL I/III/IV/V w budynku W i WW – **2500 m²**; ust. 2 – strefa ZL obejmująca część podziemną ≤ 50% (tj. 1250 m²), chyba że wyjścia z podziemia prowadzą bezpośrednio na zewnątrz (ust. 3); **ust. 4 – zakaz powiększania stref w wielokondygnacyjnych budynkach W i WW** (tryskacze/oddymianie nie pomagają).
- **§ 277 ust. 1–2:** garaż zamknięty – strefa ≤ **5000 m²**; +100% przy tryskaczach albo przy ściankach EI 30 co 2 stanowiska.
- PM inne niż garaż – § 228 (W: Q ≤ 500 MJ/m² → 5000 m²; 500–1000 → 2500 m²; przy pomieszczeniach zagrożonych wybuchem mniej). <!-- poprawione przez weryfikatora --> **§ 228 ust. 2:** strefy PM (inne niż garaż) w **podziemnej** części budynku – nie więcej niż **50%** wartości z tabeli (W, Q ≤ 500 → 2500 m²; 500–1000 → 1250 m²) – dotyczy techniki/magazynów/archiwów wydzielonych jako PM na –1/–2.

**Wniosek dla programu (szacunek):** kondygnacja skrzydeł + wieży o powierzchni wewnętrznej ≤ 2500 m² = 1 strefa; większe kondygnacje (np. parter/podium) dzielić ścianą REI 120 z drzwiami EI 60. Kondygnacje połączone pustką (hol główny parter+1, sala Sejmiku z galerią) – **suma powierzchni połączonych kondygnacji ≤ 2500 m²**.

### 4.2. Elementy oddzielenia ppoż. [P] (§ 232 WT)

| Klasa budynku „B” | Wymaganie |
|---|---|
| Ściany i stropy oddzielenia (z wyjątkiem stropów w ZL) | **REI 120** |
| Stropy oddzielenia w ZL | **REI 60** |
| Drzwi/zamknięcia w elementach oddzielenia | **EI 60** |
| Drzwi z przedsionka na korytarz / do pomieszczenia | EI 30 |
| Drzwi z przedsionka na klatkę schodową | E 30 |
| Przedsionek | ≥ **1,4 × 1,4 m**, ściany i strop EI 60, niepalne, zamykany drzwiami, wentylowany (w W – nadciśnienie, § 246 ust. 2) |
| Otwory | ≤ **15%** powierzchni ściany oddzielenia; ≤ **0,5%** powierzchni stropu oddzielenia (bez limitu dla otworów na drogach manewrowych garażu) |
| Przeszklenia w ścianie oddzielenia | ≤ 10% pow. ściany; EI 60 (obudowa drogi ewak.) lub E 60 (pozostałe) – § 232 ust. 6 |

- **§ 235:** ściana oddzielenia na własnym fundamencie lub stropie na konstrukcji o tej samej odporności; wysunięta **0,3 m** przed lico lub **pionowy pas niepalny ≥ 2 m, EI 60** na całej wysokości elewacji; przy dachu rozprzestrzeniającym ogień – 0,3 m ponad pokrycie lub pas 1 m; przy świetlikach/klapach dymowych bliżej niż 5 m – wyprowadzić 0,3 m ponad ich krawędź.
- **§ 234:** przepusty instalacyjne o klasie EI elementu; **§ 268 ust. 4–6:** klapy ppoż. EIS w przejściach kanałów, sterowane z SSP.
- **§ 210:** części wydzielone ścianami oddzielenia od fundamentu do przekrycia dachu mogą być traktowane jako odrębne budynki.

### 4.3. Atrium / przestrzenie wielokondygnacyjne
WT 2002 nie ma rozdziału o atriach. Zastosowanie mają: § 226–227 (strefa = suma połączonych kondygnacji ≤ 2500 m²), § 232 ust. 2 (otwory w stropie oddzielenia ≤ 0,5%), § 247 ust. 2 (**przekryty dziedziniec wewnętrzny** – rozwiązania zabezpieczające drogi ewakuacyjne przed zadymieniem), § 223 (pasy międzykondygnacyjne w ścianach zewnętrznych; w projekcie nowych WT także w ścianach atrium). [P][PR]

**Warianty (wniosek):**
1. **Pustka w obrębie jednej strefy** (np. hol główny parter + antresola, foyer Sejmiku 2 kondygnacje) – suma ≤ 2500 m²; oddymianie grawitacyjne/mechaniczne z sufitu pustki (SSP), napowietrzanie dołem; schody w pustce nie są drogą ewakuacyjną (chyba że mieszczą się w limitach przejść/dojść w strefie).
2. **Atrium oddzielone od kondygnacji** przeszkleniami EI 60 z drzwiami EI 60 (lub kurtynami EI – drogie) – atrium jako odrębna strefa/część jednej strefy, oddymiane.
3. **Pełne atrium przez wiele kondygnacji biurowych** – wymaga **rozwiązań zamiennych** (art. 6a ustawy ppoż.: ekspertyza + CFD + zgoda KW PSP) – **ryzyko dla konkursu** (koszt, czas, niepewność). Nie stosować jako kluczowego elementu idei.

### 4.4. Opcja: skrzydła jako odrębne budynki SW (wniosek – do decyzji)
Jeżeli skrzydła wzdłuż Mazowieckiej i Wybrzeża Słowackiego mają wysokość wg § 6 ≤ 25 m i zostaną oddzielone od wieży ścianą oddzielenia **od fundamentu do dachu** (§ 210; przez garaż – otwory na drogach manewrowych bez limitu, § 232 ust. 2), będą budynkami **SW**: klatki obudowane z drzwiami dymoszczelnymi i urządzeniami zapobiegającymi zadymieniu/oddymiającymi (§ 245 pkt 2) – **bez przedsionków**, bez obowiązku oddymiania korytarzy (§ 247 dotyczy W). Koszty: drzwi EI 60 w ścianie REI 120 na każdym połączeniu, pas elewacyjny 2 m (§ 235 ust. 2), dachy skrzydeł w pasie 8 m od ścian wieży z otworami – NRO, R 30, RE 30 (§ 218 ust. 1 i 3). Projekt nowych WT (§ 221 ust. 2) ułatwia to przy garażu z tryskaczami. **Zalecenie:** w konkursie pokazać budynek jako jedną całość W (prostsza narracja, bez ryzyka), a opcję SW opisać jako rezerwę optymalizacji kosztów.

---

## 5. Ewakuacja

### 5.1. Liczba osób – założenia (wniosek)
- Program: 403 osoby na stanowiskach urzędniczych; **każdy pokój 24 m² ma umożliwiać pracę 3 osób** (Program, s. 4) → do obliczeń ewakuacji przyjmować **3 os./pokój** (≈ 8 m²/os. pow. pokoju) + goście; ok. **540 os.** w części biurowej przy pełnym wykorzystaniu pokoi (szacunek).
- Sejmik: sala do 100 os. (+ publiczność, media); na kondygnacji Sejmiku/kancelarii także sale komisji 50 i 30 os., 4 sale klubów (2×30, 2×15), sala radnych, gabinety → **ok. 300–330 os.** na najbardziej obciążonej kondygnacji Sejmiku (jeśli wszystko na jednym poziomie).
- Strefa konferencyjna: 200 + 80 + 6 × 30 os. → **ok. 460 os.** (lokować na parterze/I piętrze z bezpośrednimi wyjściami).

### 5.2. Klatki schodowe w budynku W [P]
- **§ 246 ust. 1:** ewakuacja do **co najmniej dwóch klatek**, obudowanych i oddzielonych od poziomych dróg komunikacji i pomieszczeń **przedsionkiem przeciwpożarowym** (§ 232).
- **§ 246 ust. 2:** klatki i przedsionki dla stref innych niż ZL IV i PM – **urządzenia zapobiegające zadymieniu** (w praktyce: system różnicowania ciśnień – nadciśnienie, PN-EN 12101-6 / PN-EN 12101-13 – normy dobrowolne).
- **§ 246 ust. 4 pkt 1:** jedna klatka dopuszczalna, gdy kondygnacja ≤ 750 m² (bez ZL II) – **nie stosować** (ZL I na piętrach Sejmiku i tak wymaga dwóch kierunków; projekt nowych WT wymaga wtedy dźwigu ratowniczego).
- **§ 249 ust. 1:** obudowa klatki – klasa jak dla stropów: **REI 60** (EI 60). **Ust. 3:** biegi i spoczniki niepalne, **R 60**; **ust. 4:** wymóg R 60 nie dotyczy klatek wydzielonych na każdej kondygnacji przedsionkami (nasz przypadek), niepalność pozostaje.
- **§ 249 ust. 6:** ściana zewnętrzna klatki ewakuacyjnej a inna ściana zewnętrzna **tego samego lub innego budynku** – odległość wg § 271 (8 m), chyba że jedna z nich ma klasę jak strop (REI 60) w tym pasie. **Wniosek:** przeszklone klatki tylko na elewacjach „otwartych” (ulica, rzeka), nie w narożnikach wklęsłych podwórza.
- **§ 250 ust. 2:** w W piwnice (kondygnacje podziemne) oddzielone od klatki **przedsionkiem ppoż.**; **§ 250 ust. 1:** zabezpieczenie przed omyłkowym zejściem do podziemia (bariera/odrębny bieg).
- **§ 251:** wyjście z klatki na dach/strych – drzwi lub klapa EI 30 (SW i wyższe).
- **§ 252:** schody ruchome i pochylnie ruchome nie są drogami ewakuacyjnymi.
- **§ 244:** zakaz spoczników ze stopniami; zakaz schodów zabiegowych jako jedynej drogi; schody wachlarzowe – stopnie ≥ 0,25 m (§ 69 ust. 6).
- **§ 68 ust. 1–2:** budynek użyteczności publicznej – bieg **≥ 1,2 m**, spocznik **≥ 1,5 m**, stopień ≤ 0,175 m; łączna szerokość biegów/spoczników **0,6 m na 100 osób** z najliczniej obsadzonej kondygnacji. **§ 69:** ≤ 17 stopni w biegu; 2h + s = 0,60–0,65 m.
- **M.13 (Standardy dostępności MSWiA, załącznik Regulaminu):** biegi schodów na klatkach na drogach ewakuacyjnych **min. 1,6 m** (w każdym typie budynku), mierzone między poręczami. Regulamin (rozdz. 8 „Dostępność”) wymaga zgodności z tymi standardami → **przyjąć bieg 1,6 m** (wniosek; przewyższa WT).
- **Obliczenie kontrolne (wniosek):** kondygnacja Sejmiku ~330 os. → 0,6 × 3,3 = **1,98 m** łącznie → 2 klatki × 1,6 m = 3,2 m ✔; strefa konferencyjna ~460 os. na piętrze → 2,76 m łącznie → 2 × 1,6 m ✔ (lub parter z wyjściami bezpośrednimi).

### 5.3. Przejścia i dojścia ewakuacyjne [P]
- **§ 237 – przejście** (w pomieszczeniu, do wyjścia na drogę ewakuacyjną): ZL **40 m**; +25% w pomieszczeniach wyższych niż 5 m (sala Sejmiku, hol); +50% przy tryskaczach; +50% przy samoczynnym oddymianiu (SSP); zwiększenia sumują się (ust. 5–7); ≤ 3 pomieszczenia po drodze (ust. 8); szerokość 0,6 m/100 os., min. 0,9 m (0,8 m do 3 os.) (ust. 10); przy nieustalonej aranżacji projektowo ≤ 80% (ust. 4).
- **§ 256 – dojście** (od wyjścia z pomieszczenia do wyjścia do innej strefy, na zewnątrz albo do obudowanej klatki – ust. 2), mierzone **w osi drogi do pierwszych drzwi przedsionka** (ust. 1):

| Strefa | 1 kierunek | ≥ 2 kierunki | z tryskaczami (+50%) | tryskacze + oddymianie drogi (+100%) |
|---|---|---|---|---|
| **ZL I** (Sejmik, sale konf.) | **10 m** | **40 m** | 15 / 60 m | 20 / 80 m |
| **ZL III** (biura) | **30 m** (w tym ≤ 20 m poziomo) | **60 m** | 45 / 90 m | 60 / 120 m |
| PM Q ≤ 500 (garaż, technika) | 60 m (≤ 20 m poziomo) | 100 m | — | — |

- Przypis 1 tabeli § 256: drugie dojście może być dłuższe o 100% od najkrótszego; dojścia nie mogą się pokrywać ani krzyżować (wspólny początek ≤ 2 m).
- **Wniosek:** (a) projektować bez „podpierania się” zwiększeniami: ślepe końce korytarzy ZL III ≤ 20 m poziomo, ZL I ≤ 10 m; (b) oddymianie korytarzy wymagane przez § 247 ust. 1 – jeśli wykonane jako **samoczynne oddymianie sterowane SSP**, może być podstawą +50% (interpretacja do potwierdzenia z rzeczoznawcą; nadciśnienie korytarza nie jest „oddymianiem”); (c) zwiększenie limitu 20 m „na poziomej drodze” – interpretacja niejednolita, nie zakładać.

### 5.4. Szerokości, drzwi, korytarze [P]
- **§ 239:** drzwi z pomieszczeń – 0,6 m/100 os., min. **0,9 m** (0,8 m do 3 os.); otwierane na zewnątrz z pomieszczeń > 50 os. (ust. 2 pkt 3); **drzwi wyjściowe z budynku i z klatki na zewnątrz – nie węższe niż bieg** (ust. 4) → przy biegu 1,6 m drzwi ≥ 1,6 m (np. 2-skrzydłowe z jednym skrzydłem ≥ 0,9 m, § 240 ust. 1). <!-- poprawione przez weryfikatora --> *Uwaga:* § 239 ust. 4 odsyła do szerokości biegu „określonej zgodnie z § 68 ust. 1 i 2” (min. 1,2 m lub 0,6 m/100 os.), a nie do szerokości przyjętej projektowo; przyjęcie drzwi ≥ 1,6 m przy biegu 1,6 m (M.13) to założenie konserwatywne (wniosek).
- **§ 236 ust. 4:** drzwi wyjściowe z budynku dla > 50 os. **otwierane na zewnątrz** (wyjątek tylko dla budynków wpisanych do rejestru – nas nie dotyczy).
- **§ 240:** zakaz drzwi obrotowych i podnoszonych na drogach ewakuacyjnych (ust. 3) – przy wejściu głównym drzwi obrotowe tylko z dodatkowymi drzwiami ewakuacyjnymi obok; drzwi rozsuwane – automatyczne z otwarciem awaryjnym (ust. 4); samozamykacze w drzwiach o klasie EI/S (ust. 6); **urządzenia przeciwpaniczne** dla pomieszczeń > 300 os. (ust. 7).
- **§ 242:** poziome drogi – 0,6 m/100 os., **min. 1,4 m** (1,2 m do 20 os.); wysokość 2,2 m (lokalnie 2,0 m na ≤ 1,5 m/10 m); skrzydła drzwi nie zawężają drogi (poza samozamykającymi).
- **§ 243:** korytarze ZL dzielone co **50 m** drzwiami dymoszczelnymi (chyba że korytarz zabezpieczony przed zadymieniem); przegrody nad sufitem i pod podłogą podniesioną niepalne.
- **§ 241:** obudowa poziomych dróg – jak ściany wewnętrzne, min. **EI 30** dla „B” (EI 15 minimum ogólne); naświetla nieotwierane > 2 m w ZL III dopuszczalne (ust. 2).
- **§ 256 ust. 6 – ewakuacja przez hol** (potwierdzona przez Organizatora, odp. na pyt. 78, Wyjaśnienia nr 20): tylko z **jednej** klatki na hol; hol oddzielony od poziomych dróg jak klatka; szerokość drogi w holu **+50%** względem § 242; wysokość holu na drodze **≥ 3,3 m**; drzwi zewnętrzne **+50%** względem § 239 ust. 4. Pozostałe klatki – wyjścia bezpośrednio na zewnątrz.
- Dostępność: M.13 zaleca drzwi ewakuacyjne wyróżnione na tle ściany, przyciski automatycznego otwierania ciężkich drzwi ppoż. (0,8–1,0 m), a poręcze nie mogą zawężać szerokości wymaganej przepisami ppoż.; w systemach nadciśnieniowych siła otwarcia drzwi bywa do 100 N → **napędy drzwi klatek/przedsionków sterowane z SSP** (wniosek).

### 5.5. Pomieszczenia zgromadzeń (sala Sejmiku, sale konferencyjne) [P]
- **§ 238:** ≥ **2 wyjścia** oddalone ≥ **5 m** z pomieszczeń > 50 os. lub > 300 m² w ZL.
- **§ 260 ust. 1:** w pomieszczeniach > 50 os. zakaz łatwo zapalnych przegród, stałego wyposażenia, wystroju i wykładzin.
- **§ 261** (pomieszczenia > 200 os. z miejscami w rzędach): siedzenia trudno zapalne, odstęp 0,45 m, ≤ 16 miejsc między przejściami / 8 przy ścianie, przejścia ≥ 1,2 m (do 150 os.), rzędy mocowane. Sala Sejmiku (100) – formalnie nie, sala 200-os. – na granicy („ponad 200”). **Wniosek:** stosować § 261 w obu salach (amfiteatr Sejmiku z przejściami 1,2 m, stopnie równe, podświetlone krawędzie, poręcze; miejsca dla wózków na poziomach wejść).
- **§ 181 ust. 3 pkt 1 lit. b:** oświetlenie ewakuacyjne w salach konferencyjnych > 200 os.; pkt 2 lit. d – na drogach ewakuacyjnych w wysokich budynkach użyteczności publicznej (czyli wszędzie) – ≥ 1 h (ust. 5), PN-EN 1838.
- **§ 216 ust. 7:** galeria/antresola dla > 10 os. (np. galeria publiczności) – konstrukcja wg klasy budynku („B”).
- Galeria publiczności z oddzielnym wejściem (Program) daje naturalne **drugie wyjście** – prowadzić je do drugiej klatki.

### 5.6. Zabezpieczenie dróg ewakuacyjnych przed zadymieniem (W) [P]
- **§ 247 ust. 1:** w budynku W w strefach innych niż ZL IV – **rozwiązania techniczno-budowlane zabezpieczające przed zadymieniem poziomych dróg ewakuacyjnych** (oddymianie mechaniczne korytarzy z napowietrzaniem, ew. nadciśnienie korytarzy).
- **§ 247 ust. 2:** przekryty dziedziniec wewnętrzny (atrium) – zabezpieczenie dróg ewakuacyjnych przed zadymieniem.
- **§ 247 ust. 3:** kondygnacja podziemna z pomieszczeniem > 100 os. – usuwanie dymu z pomieszczenia i dróg (dot. MDS/„schronu”, jeśli traktowany jako pomieszczenie dla > 100 os. – wniosek).
- **§ 270:** wymagania dla instalacji wentylacji oddymiającej (kanały E600S/EIS, klapy E600S AA/EIS AA, wentylatory F400 120 lub F600 60, klapy dymowe B300 30/B600 30).
- **Wniosek przestrzenny:** w każdym trzonie: szacht nawiewu nadciśnienia klatki (~0,6–1,0 m²), szacht nadciśnienia przedsionków/dźwigu ratowniczego, szacht oddymiania korytarzy (~0,8–1,5 m²) + upusty/napowietrzanie; wentylatory na dachu (strefa techniczna) – oddalone od czerpni powietrza do nadciśnienia.

### 5.7. Ewakuacja osób z niepełnosprawnościami – MOE (wymóg Regulaminu) [O]+[PR]
**Wymagania wiążące:**
- Regulamin, rozdz. 8 „Dostępność”: miejsca oczekiwania na ewakuację dla osób na wózkach **na klatkach schodowych, w poziomie podestów kondygnacyjnych**; **nie mogą zawężać** wymaganej szerokości drogi ewakuacyjnej; **miejsce na krzesło ewakuacyjne**; w rejonie MOE **interkom dwustronny** z ochroną i stanowiskiem strażaka kierującego akcją gaśniczą. Program (s. 11): klatki poprzedzone przedsionkami ppoż.; MOE z zachowaniem wymaganych wymiarów; interkom.
- Ustawa o dostępności, **art. 6 pkt 1 lit. e** – możliwość ewakuacji lub uratowania osób ze szczególnymi potrzebami [S8].
- M.13 – odesłanie do poradnika „Dostępność. Bezpieczna Ewakuacja” (Fundacja Polska bez Barier, 2022) [Regulamin, zał. M.13].

**Wymagania z projektu nowych WT [PR] (zalecane do spełnienia):** § 252 ust. 1 pkt 4 – klatka schodowa z wyznaczonymi **punktami oczekiwania** (obrys na posadzce, zał. 11 projektu), EVCS z monitoringiem usterek, oświetlenie ≥ 5 lx, drzwi ≥ 0,9 m z zamknięciem przeciwpanicznym ≤ 1,2 m i siłą ≤ 25 N lub automatem; § 258 – dojście do MOE ≤ 20 m (w ZL I – ≤ 10 m), dostęp ratowników ≤ 10 m od drzwi klatki/przedsionka dźwigu ratowniczego; § 253 – dźwig ewakuacyjny wg PN-EN 81-76 z punktami 1,5 × 0,9 m w przedsionku.

**Specyfikacja koncepcyjna (wniosek):**
- Na każdym podeście kondygnacyjnym każdej klatki ewakuacyjnej: **pole MOE 0,9 × 1,4 m** (praktyka BS 9999; projekt WT dla przedsionka dźwigu: 1,5 × 0,9 m) **poza** szerokością biegu/spocznika (spocznik = 1,6 m wolne + MOE w poszerzeniu) + **wnęka na krzesło ewakuacyjne** + panel EVCS (interkom) + oznakowanie.
- Alternatywnie/uzupełniająco – MOE w przedsionku wspólnym klatki i dźwigu ratowniczo-ewakuacyjnego (przedsionek ~2,4 × 3,0 m).
- Co najmniej **jeden dźwig ratowniczy pełniący też funkcję dźwigu ewakuacyjnego OzN** (PN-EN 81-76) w każdym trzonie wieży; zasilanie z dwóch źródeł + agregat.
- Sygnalizatory optyczne alarmu (PN-EN 54-23) w toaletach i przestrzeniach ogólnodostępnych – dla osób niesłyszących (dobra praktyka zgodna z M.13).

---

## 6. Dźwig dla ekip ratowniczych [P]
- **§ 253 ust. 1 WT:** w budynku ZL I/II/III/V z kondygnacją, której posadzka jest **> 25 m** nad terenem przy najniżej położonym wejściu – **co najmniej 1 dźwig dla ekip ratowniczych**, zgodny z PN dot. dźwigów dla straży pożarnej (zał. 1 WT: **PN-EN 81-72:2005**; aktualna edycja normy – nowsza, do stosowania w porozumieniu z rzeczoznawcą); dostęp do **każdej strefy pożarowej na kondygnacji** bezpośrednio lub drogami komunikacji ogólnej.
- **Ust. 2:** dojście przez **przedsionek przeciwpożarowy** (§ 232). **Ust. 3:** ściany i stropy szybu – jak stropy budynku (**REI 60**). **Ust. 4:** szyb z **urządzeniami zapobiegającymi zadymieniu** (nadciśnienie).
- **§ 193 ust. 4 WT** – odesłanie do § 253 i przepisów ppoż.
- **Rozp. 2009 § 12 ust. 5:** każdy dźwig ratowniczy połączony z drogą pożarową **dojściem ≤ 50 m, szer. ≥ 1,5 m**, przy czym długość obejmuje także drogę ewakuacyjną w budynku [S13].
- Wymagania normowe (PN-EN 81-72, dobrowolne – parametry orientacyjne): kabina min. 1100 × 1400 mm / 630 kg, przy przewozie noszy 1100 × 2100 mm / 1000 kg; drzwi ≥ 800 mm; obsługa wszystkich kondygnacji; dojazd na najwyższy przystanek ≤ 60 s; ochrona przed wodą; zasilanie rezerwowe.
- Projekt nowych WT (§ 267) [PR]: jw. + obowiązek także przy ≥ 3 kondygnacjach podziemnych.
- **Wniosek:** 1 dźwig ratowniczy w trzonie wieży (zjazd do garażu), wejście z poziomu dostępu PSP **od strony drogi pożarowej** (Wybrzeże Słowackiego/Mazowiecka) w odległości ≤ 50 m; drugi – zalecany w drugim trzonie (redundancja, ewakuacja OzN z obu kierunków). Przedsionek dźwigu może być wspólny z przedsionkiem klatki (praktyka spotykana – do potwierdzenia z rzeczoznawcą); zawory 52 w przedsionku.

---

## 7. Instalacje i urządzenia przeciwpożarowe

### 7.1. System sygnalizacji pożarowej (SSP) [O]
- **Rozp. 2010 § 28 ust. 1 pkt 10:** wymagany w **budynkach użyteczności publicznej wysokich i wysokościowych** → cały budynek; pkt 17 – garaże podziemne > 1500 m² lub > 1 kondygnacja podziemna (i tak objęte). Pkt 15 – ośrodki elektronicznego przetwarzania danych o zasięgu wojewódzkim (serwerownia) – objęta SSP.
- SSP steruje: nadciśnieniem, oddymianiem, klapami ppoż. (§ 268 ust. 6 WT), drzwiami (zwalniacze, napędy), dźwigami (zjazd), DSO, kontrolą dostępu.

### 7.2. Dźwiękowy system ostrzegawczy (DSO) [O]
- **Rozp. 2010 § 29 ust. 1 pkt 5:** budynki użyteczności publicznej wysokie → **obowiązkowy**; ust. 2 – w obiekcie z DSO nie stosuje się innych akustycznych sygnalizatorów pożarowych dla użytkowników. Głośniki we wszystkich pomieszczeniach i na drogach; strefowanie zgodne ze strefami pożarowymi; mikrofon strażaka w centrum bezpieczeństwa. Integracja z pętlami indukcyjnymi (wymóg Regulaminu) – rozważyć (wniosek).

### 7.3. Stałe urządzenia gaśnicze (SUG, tryskacze) [O]
- **Rozp. 2010 § 27 ust. 2:** tryskacze obowiązkowe m.in. w **budynkach użyteczności publicznej wysokościowych (WW)** – **nie w W**; ust. 1: SUG (gazowe/inne) w archiwach wyznaczonych przez Naczelnego Dyrektora Archiwów Państwowych, muzeach/zabytkach wyznaczonych przez GKZ, ośrodkach EPD o znaczeniu krajowym.
- **WT § 277 ust. 3:** tryskacze w garażu zamkniętym obejmującym **> 2 kondygnacje podziemne** lub poniżej II kondygnacji podziemnej (Program: **2** kondygnacje podziemne → nie obowiązkowe).
- **Korzyści z tryskaczy w budynku W (WT):** dojścia +50% (§ 256 ust. 4), przejścia +50% (§ 237 ust. 6), odległości do sąsiadów –25% (tylko nasz budynek, § 271 ust. 7) lub –50% (oba), czas ciągłości zasilania kabli 30 min (§ 187 ust. 7), <!-- poprawione przez weryfikatora --> (*nie* jest to oszczędność wody: wg rozp. 2009 § 7 ust. 1 pkt 2 przy tryskaczach wymagana ilość wody = woda dla tryskaczy + 50% wody do gaszenia zewnętrznego, nie mniej niż woda do gaszenia zewnętrznego), garaż: strefa ×2 (§ 277 ust. 2), kanały oddymiania tylko E (§ 277 ust. 5). **Brak** korzyści: powierzchnia strefy (§ 227 ust. 4), klasa odporności (§ 214).
- Projekt nowych WT: zwolnienie z pasów międzykondygnacyjnych (§ 234 ust. 4), odrębne budynki nad garażem z tryskaczami (§ 221 ust. 2) [PR].
- **Rekomendacja (wniosek):** **instalacja tryskaczowa w całym budynku** (PN-EN 12845 lub VdS; biura OH1, garaż OH2/OH3) – uelastycznia plan (dłuższe ślepe korytarze, otwarte strefy wspólne, foyer), ułatwia relację z WS5, jest dobrze odbierana przez sąd (bezpieczeństwo, ubezpieczenie, pożary pojazdów elektrycznych w MDS/garażu). Zarezerwować: zbiornik tryskaczowy + pompownia (odrębna strefa pożarowa, § 212 ust. 9). Serwerownia i archiwum PZGiK – **gaszenie gazem** (IG-55/IG-541 lub FK-5-1-12) – dobra praktyka.

### 7.4. Instalacja wodociągowa przeciwpożarowa (hydranty wewnętrzne) [O]
- **Rozp. 2010 § 19 ust. 1 pkt 1:** **hydranty 25** na każdej kondygnacji budynku W (strefy ZL); **ust. 2:** **hydranty 33** w garażu wielokondygnacyjnym lub <!-- poprawione przez weryfikatora --> jednokondygnacyjnym zamkniętym > 10 stanowisk; **ust. 6:** **zawory 52** w budynkach W o > 1 kondygnacji nadziemnej.
- **§ 20 ust. 1 pkt 1:** przy wejściach do klatek na każdej kondygnacji – zawory 52 **zaleca się w przedsionkach ppoż.**, dopuszcza na klatkach; **ust. 2:** po **dwa zawory 52 na każdym pionie** na kondygnacjach podziemnych i położonych > 25 m, po jednym na pozostałych; **ust. 3:** zasięg – długość węża + 3 m prądu rozproszonego (ZL, budynki wielokondygnacyjne).
- **§ 21:** zawory na wys. 1,35 ± 0,1 m; § 22: wydajność hydrant 25 – 1,0 dm³/s, 33 – 1,5, zawór 52 – 2,5 dm³/s, ciśnienie ≥ 0,2 MPa, max 0,7 MPa na zaworach 52.
- **§ 23 pkt 3 lit. a:** jednoczesny pobór z **4** sąsiednich hydrantów/zaworów 52 na kondygnacjach podziemnych i > 25 m.
- **§ 24 ust. 2–5:** w budynkach W zapas wody ≥ **100 m³** wyłącznie na ten cel; redukcje: do 50 m³ (brak stref > 750 m² – u nas raczej nie), do **50 m³ przy zasilaniu zbiornika z sieci ≥ 10 dm³/s**, do **25 m³ przy ≥ 15 dm³/s** – warunek: **dodatkowa nasada 75 mm na elewacji od strony drogi pożarowej** (ust. 5).
- **§ 25:** piony w klatkach lub przy nich; w W z ≥ 2 klatkami piony **połączone na najwyższej kondygnacji (≥ DN 80)**; zawory 52 na pionach **DN 80**; przewody obwodowe przy > 3 pionach; przewody palne obudowane EI 60.
- **Wniosek przestrzenny:** pomieszczenie zbiornika (25–100 m³) i pompowni hydrantowej w –1/–2 jako odrębna strefa (§ 212 ust. 9 WT); nasady 75 mm na elewacji frontowej przy wejściu dla PSP.

### 7.5. Zaopatrzenie wodne zewnętrzne [O]
- **Rozp. 2009 § 3 ust. 1 pkt 1, § 5 ust. 1 pkt 2:** budynek użyteczności publicznej > 5000 m³ lub > 1000 m² – **20 dm³/s z co najmniej dwóch hydrantów DN 80** (lub 200 m³ w zbiorniku).
- **§ 10 ust. 6:** hydranty wzdłuż ulic, odległość między hydrantami ≤ 150 m, od krawędzi jezdni ≤ 15 m, **najbliższy od obiektu ≤ 75 m**, pozostałe ≤ 150 m, **od ściany budynku ≥ 5 m**; § 10 ust. 8: DN 80 nadziemny – 10 dm³/s przy 0,2 MPa.
- **Wniosek:** potwierdzić z MPWiK Wrocław wydajność sieci w Mazowieckiej/Wybrzeżu Słowackiego; w koncepcji pokazać 2 hydranty zewnętrzne na planie zagospodarowania.

### 7.6. Zasilanie, oświetlenie, kable, wyłącznik ppoż. [P]
- **§ 181 ust. 1 WT:** zasilanie z **dwóch niezależnych, samoczynnie załączających się źródeł** + samoczynne oświetlenie awaryjne (budynek, w którym zanik napięcia zagraża życiu) – Program przewiduje agregat i UPS ✔.
- **§ 183 ust. 2–4:** **przeciwpożarowy wyłącznik prądu** dla stref > 1000 m³, przy głównym wejściu lub złączu, oznakowany; jego użycie nie może załączać agregatu (poza oświetleniem awaryjnym).
- **§ 187 ust. 3, 5, 7:** zespoły kablowe urządzeń ppoż. z ciągłością działania na wymagany czas (PH/E – np. PH90/E90), w strefach z tryskaczami dopuszczalne 30 min.
- **§ 182:** trafostacja w budynku – odległość ≥ 2,8 m od pomieszczeń stałego pobytu, ściany/stropy jako oddzielenia ppoż.
- **§ 268 ust. 1 pkt 5:** maszynownie wentylacji/klimatyzacji – ściany **EI 60**, drzwi **EI 30** (nie dot. urządzeń ponad dachem).
- **§ 220:** kotłownia gazowa > 30 kW w W – EI 120 / REI 120 / drzwi EI 60 (w budynku zeroemisyjnym z pompami ciepła zapewne nie wystąpi – wniosek).
- **§ 259:** podłoga podniesiona > 0,2 m (serwerownia) – konstrukcja niepalna, REI 30, sektory ≤ 1000 m².
- **§ 262:** sufity podwieszone niepalne/niezapalne, niekapiące; przestrzeń nad sufitem dzielona co 1000 m² i w korytarzach co 50 m.
- **§ 258:** w strefach ZL zakaz materiałów wykończeniowych łatwo zapalnych, bardzo toksycznych lub intensywnie dymiących; na drogach ewakuacyjnych zakaz łatwo zapalnych.

### 7.7. Fotowoltaika i magazyn energii
- **Pb art. 29 ust. 4 pkt 3 lit. c [O]:** urządzenia PV > 6,5 kW – **uzgodnienie projektu z rzeczoznawcą ppoż.** i zawiadomienie PSP o zakończeniu instalacji (z planem PV dla ekip ratowniczych) [S7].
- **Projekt WT [PR]:** przewody DC na zewnątrz budynku lub w osłonie EI 60 (W), **wyłącznik awaryjny PV** w miejscu dostępu ratowników (§ 303–304); BESS – rozdz. 2.3.
- **Wniosek – BIPV na elewacji powyżej 25 m:** moduły z folią EVA/PVB zwykle nie są A1/A2 → jako „okładzina elewacyjna” kolidują z § 216 ust. 8 WT (projekt WT dopuszcza folie w szybach laminowanych tylko przy zapewnionym NRO). PV elewacyjne – **≤ 25 m** lub w przeszkleniach o potwierdzonej klasyfikacji; główny potencjał PV – dach (uwaga na § 216 tab. przypis 3, § 218, § 219).

### 7.8. Centrum bezpieczeństwa (wniosek)
Przy wejściu głównym od strony drogi pożarowej: pomieszczenie ochrony z centralą SSP, centralą DSO, stacją EVCS (interkomy z MOE – wymóg Regulaminu), panelem PSP, klucznicą, wyłącznikiem ppoż. prądu, wyłącznikami awaryjnymi PV/BESS; widoczność na hol; bezpośredni dostęp z zewnątrz.

---

## 8. Garaż podziemny (2 kondygnacje) [P]/[O]

| Wymaganie | Podstawa | Wartość |
|---|---|---|
| Kategoria / klasa | WT § 209 ust. 3, § 275 ust. 1, § 212 ust. 4 i 7 | PM, Q ≤ 500 MJ/m²; klasa „B” (pod budynkiem W) |
| Strefa pożarowa | § 277 ust. 1–2 | ≤ 5000 m² (+100% z tryskaczami) |
| Tryskacze | § 277 ust. 3 | obowiązkowe przy > 2 kondygnacjach podziemnych lub poniżej II – **u nas nie** (rekomendowane) |
| Wentylacja oddymiająca | § 277 ust. 4 | gdy strefa nie ma bezpośredniego wjazdu/wyjazdu **lub** > 1500 m² → praktycznie **tak** (strumieniowa lub kanałowa, SSP) |
| SSP | rozp. 2010 § 28 ust. 1 pkt 17 | > 1500 m² lub > 1 kondygnacja podziemna |
| Hydranty | rozp. 2010 § 19 ust. 2 | hydranty 33 |
| Wyjścia ewakuacyjne | § 278 ust. 1–4 | ≥ 2 (gdy > 25 stanowisk i brak oddymiania lub > 1500 m²), jedno może być wjazdem; przy strefie > 2 kondygnacji – na każdej; przejście do wyjścia ≤ **40 m** (+50% tryskacze; +50% oddymianie – **nie** przy wentylacji strumieniowej); wyjście dostępne przy zamkniętej bramie |
| Podział stref | § 278 ust. 6 | strefy > 1500 m² – możliwość oddzielenia od siebie i od części nadziemnej zamknięciami ≥ EI 30 |
| Połączenie z budynkiem | § 280 ust. 1–2; § 250 ust. 2 | **przedsionek ppoż. z drzwiami EI 30**; przed dźwigiem zamiast przedsionka drzwi EI 60 (§ 280 ust. 2) – ale dźwig ratowniczy zawsze przez przedsionek (§ 253 ust. 2); klatki budynku W – przedsionek na poziomach podziemnych |
| Wrota a okna | § 279 | pionowo ≥ 1,5 m (1,1 m z daszkiem 0,6 m) od okien; w rzucie ≥ 1,5 m od okien pomieszczeń na pobyt ludzi |
| Wysokość, wjazdy | § 102 | 2,2 m w świetle konstrukcji, 2,0 m pod instalacjami; wrota ≥ 2,3 × 2,0 m |
| Pochylnie | § 70, § 103 | wewn./pod dachem: 20% (garaż 1–2-poziomowy), 15% (wielopoziomowy); zewn. bez przekrycia 15%; > 25 aut/kondygnację: 5,5 m dwukierunkowa lub 2 × 2,7 m |
| Zakazy | § 281 | studzienki rewizyjne, przewody gazowe, otwory od palenisk/kanałów – zakazane |
| Uzgodnienie | rozp. 2023 § 3 ust. 1 pkt 6 | garaż wielokondygnacyjny – wymaga uzgodnienia z rzeczoznawcą |

**Ładowanie pojazdów elektrycznych:** w WT 2002 i rozp. 2010 brak przepisów szczególnych. Istnieją **wytyczne branżowe** (CNBOP-PIB / KG PSP / PSPA) dot. ochrony ppoż. garaży z ładowaniem EV – *źródło wtórne, treści nie weryfikowano* [W3]. **Wniosek:** stanowiska z ładowarkami blisko wjazdu i wyjść, w zasięgu dojazdu PSP, w strefie objętej tryskaczami i oddymianiem; wyłącznik awaryjny ładowarek przy wjeździe i w centrum bezpieczeństwa.

---

## 9. Elewacje [P]

- **§ 216 ust. 2 + § 208a ust. 3:** ściany zewnętrzne **NRO** przy działaniu ognia od wewnątrz i od zewnątrz (badanie wg **PN-B-02867:2013** – zał. 1 WT); klasy reakcji na ogień wg PN-EN 13501-1 (zał. 3 WT).
- **§ 216 ust. 1, tab. + przypis 2:** ściana zewnętrzna w klasie „B” – **EI 60 (o↔i)**; klasa dotyczy **pasa międzykondygnacyjnego wraz z połączeniem ze stropem**.
- **§ 216 ust. 8:** **powyżej 25 m** od poziomu terenu – okładzina elewacyjna, jej zamocowanie mechaniczne i izolacja cieplna **z materiałów niepalnych** (A1, A2). Projekt WT: **A1 lub A2,d0** (§ 227 ust. 9) [PR].
- **§ 223:** pasy międzykondygnacyjne **≥ 0,8 m**; równoważnie: daszki/gzymsy/balkony o wysięgu ≥ 0,5 m lub kombinacja wysięgu i wymiaru pionowego ≥ 0,8 m; elementy poziome EI jak ściana (EI 60) i NRO; **nie dotyczy ścian holu i dróg komunikacji ogólnej** (ust. 4) → przeszklony hol i klatki mogą być w pełni przeszklone (z zastrzeżeniem § 249 ust. 6 i § 271).
- **§ 224:** nad strefą **PM o Q > 1000 MJ/m²** – pas **1,2 m** (lub wysięg 0,8 m / suma 1,2 m). U nas dotyczy tylko ewentualnych stref PM nad terenem z dużym obciążeniem (np. archiwa wydzielone jako PM, magazyny) – wniosek: unikać takich stref pod przeszklonymi elewacjami lub zapewnić 1,2 m.
- **§ 225:** okładziny mocowane tak, by **nie odpadały** w czasie krótszym niż klasa EI ściany (60 min) → kotwy mechaniczne ze stali nierdzewnej; okładziny ceramiczne/kamienne/GRC tylko na mocowaniach mechanicznych (nie wyłącznie klejonych).
- **§ 292:** daszki nad wejściami w budynkach > 2 kondygnacji: szerokość = drzwi + 1 m, wysięg ≥ 1,5 m (W), konstrukcja przenosząca upadek okładzin/szyb (bezpieczeństwo użytkowania – wiąże się z elewacją).

**Wnioski projektowe dla elewacji (do zespołu „elewacje/wizualizacje”):**
1. Elewacja wentylowana: okładzina **A1** (cegła/klinkier, ceramika, kamień, aluminium/stal, GRC/UHPC), wełna mineralna A1, podkonstrukcja stalowa/aluminiowa – spełnia WT 2002 i projekt WT na całej wysokości.
2. Ściany kurtynowe/okna: **pas 0,8 m EI 60** za szkłem (spandrel z wełną i blachą, EI 60 wraz z połączeniem ze stropem – „fire stop” na krawędzi stropu) lub wysunięte poziome lamele/gzymsy EI 60 o wysięgu ≥ 0,5 m (mogą być atutem plastycznym rytmu poziomego – nawiązanie do gzymsów kamienic).
3. Drewno na elewacji – tylko ≤ 25 m i tylko w systemie NRO (najlepiej zrezygnować lub stosować imitacje A2).
4. Ściany zwrócone do sąsiadów (WS5, MZ19) – udział części „pełnej” EI 60 **> 65%** powierzchni ściany (§ 271 ust. 1) – inaczej rosną odległości (rozdz. 11).
5. Zielone ściany/pnącza na elewacji W – tylko z NRO podłożem i nad 25 m – unikać (palność biomasy; brak podstaw w WT).

---

## 10. Dachy [P]

- **§ 216 ust. 1:** konstrukcja dachu **R 30**, przekrycie **RE 30**; przypis 3 – wymagania nie dotyczą świetlików/naświetli ≤ 20% połaci, ani budynku, w którym nad najwyższą kondygnacją jest strop spełniający wymagania stropu (REI 60).
- **§ 216 ust. 2 + zał. 3 pkt 4:** przekrycie dachu **NRO = klasa BROOF(t1)**.
- **§ 219 ust. 1:** przekrycie dachu > 1000 m² – NRO, palna izolacja oddzielona przegrodą ≥ RE 15.
- **§ 218 ust. 1–3:** dach budynku/części **niższej**, usytuowanej bliżej niż 8 m lub przylegającej do ściany z **otworami** budynku wyższego – w pasie 8 m od tej ściany: przekrycie NRO, konstrukcja R 30, przekrycie RE 30; nie dotyczy, gdy najbliższy otwór jest **≥ 10 m nad dachem niższym** i Q ≤ 2000 MJ/m² (ust. 2); dotyczy też niższej części tego samego budynku stanowiącej odrębną strefę (ust. 3).
- **§ 235 ust. 3–4:** ściany oddzielenia ponad dach przy dachu rozprzestrzeniającym ogień; przy świetlikach/klapach dymowych < 5 m.
- **Wnioski:** (a) **dachy zielone/tarasy** na stropach żelbetowych: warstwa wegetacyjna nie może pogorszyć BROOF(t1) – pasy żwirowe 0,5–1,0 m wokół attyk, przebić, urządzeń, przy ścianach wyższych części (dobra praktyka FLL/DIN 4102-7); (b) **taras użytkowy** (np. przy Sejmiku) – część strefy pożarowej, wymaga dróg ewakuacyjnych do dwóch klatek, balustrada; klatki wyprowadzone na dach muszą zachować działanie nadciśnienia; (c) strefa techniczna na dachu: wentylatory oddymiające (F400 120/F600 60) oddalone od czerpni nadciśnienia i od elewacji z oknami.

---

## 11. Sąsiedztwo: odległości, przyleganie, ściany oddzielenia [P]

### 11.1. Reguły
- **§ 271 ust. 1:** odległość ZL–ZL (ściany niebędące ścianami oddzielenia, mające na > 65% powierzchni klasę E wymaganą dla ściany zewnętrznej, tu E 60) – **8 m**.
- **ust. 2:** ściana lub dach rozprzestrzeniające ogień – +50% (jedna) / +100% (obie).
- **ust. 4–5:** ściana z częścią „E” 30–65% → **+50% (12 m)**; < 30% → **+100% (16 m)**.
- **ust. 6–7:** tryskacze we wszystkich strefach przylegających do ścian obu budynków – **–50%**; tylko w jednym budynku – **–25%**.
- **ust. 10–12:** w pasie terenu o szerokości z ust. 1–7 ściany innego budynku muszą spełniać wymagania ścian oddzielenia (§ 232 ust. 4–5) dla obu budynków; pas o połowę węższy przy kącie 60–120°; **nie dotyczy**, gdy budynki oddziela ściana oddzielenia ppoż. spełniająca wymagania dla obu (ust. 12 pkt 1) lub kąt ≥ 120° (pkt 2).
- **§ 272 ust. 1:** od granicy **niezabudowanej działki budowlanej** – ≥ połowa odległości z § 271 (zakładając budynek wg MPZP); **ust. 3:** budynek przy granicy – od strony sąsiada **ściana oddzielenia ppoż.** (klasa wg § 232 ust. 4–5 → REI 120 dla „B”).
- **§ 12 ust. 3 WT** (zm. Dz.U. 2023 poz. 2442): budowa bezpośrednio przy granicy, gdy budynek przylega całą długością ściany do ściany budynku istniejącego na sąsiedniej działce i wysokość zgodna z MPZP – z uwzględnieniem m.in. § 271–273.
- **§ 249 ust. 6:** ściany klatek ewakuacyjnych – odległości wg § 271 (patrz 5.2).

### 11.2. Zastosowanie do sąsiadów (wniosek)

| Sąsiad | Stan | Wymaganie dla koncepcji |
|---|---|---|
| **Mazowiecka 19** (kamienica, zasób gminny; nasz budynek ma przylegać tworząc pierzeję – Program, s. 3) | okna łazienek w ścianie szczytowej – Zamawiający **zakłada ich likwidację** (odp. na pyt. 13, Wyjaśnienia nr 3; Regulamin rozdz. 7); Zamawiający **zaleca pokazanie potencjału przyszłego połączenia funkcjonalnego** z MZ19 (ta sama odpowiedź) | nasza ściana na styku = **ściana oddzielenia REI 120**, NRO, bez otworów, na własnym fundamencie (§ 235 ust. 1; uwaga na fundamenty MZ19 – podbicie/ściana szczelinowa); na elewacji frontowej przy styku **pas niepalny ≥ 2 m EI 60** (bez okien) albo wysunięcie ściany 0,3 m (§ 235 ust. 2) – interpretacja: przy braku możliwości ingerencji w elewację MZ19 cały pas po naszej stronie; **nad dachem MZ19**: w pasie 8 m od krawędzi jej dachu – **brak otworów do wysokości 10 m nad tym dachem** albo ściana jak oddzielenia (§ 218 ust. 1–2; <!-- poprawione przez weryfikatora --> formalnie § 218 wymaga NRO/R 30/RE 30 od dachu MZ19 w pasie 8 m przy otworach w naszej ścianie bliżej niż 10 m nad tym dachem – brak otworów to sposób, by nie ingerować w dach sąsiada; wniosek). Konieczne ustalenie z Inwestorem: zamurowanie okien MZ19 musi nastąpić przed odbiorem (warunek § 271/§ 272). **Przyszłe połączenie z MZ19:** zaprojektować ścianę z rezerwą na otwory zamykane drzwiami **EI 60** (łącznie ≤ 15% powierzchni ściany oddzielenia, § 232 ust. 2) na poziomach zbieżnych ze stropami kamienicy. |
| **Wybrzeże Słowackiego 5** (kamienica; oddzielona działką 10/2; połączenia nie przewiduje się – Program, s. 3) | okna w ścianie szczytowej (pokój 1 p., łazienki 2–3 p., kuchnie) – **Zamawiający nie dopuszcza ich zamurowania**; szczególna uwaga na pokój w mieszkaniu nr 6 na I piętrze (odp. na pyt. 13, Wyjaśnienia nr 3) | odległość naszej ściany od ściany szczytowej WS5: **≥ 8 m**, gdy nasza ściana ma > 65% części pełnej EI 60 (i ściana WS5 też – do sprawdzenia na inwentaryzacji M.08); **≥ 12 m** przy 30–65%; **≥ 16 m** przy < 30% (np. pełne przeszklenie); z tryskaczami w naszym budynku –25% (6 / 9 / 12 m). Alternatywa: nasza ściana zwrócona do WS5 jako **ściana oddzielenia REI 120 bez otworów** (§ 271 ust. 12 pkt 1 – stosowanie do ścian niestykających się to interpretacja do potwierdzenia z rzeczoznawcą) – akceptowalna ppoż., ale uwaga na § 13 (przesłanianie) i § 60 (nasłonecznienie) – i tak decydujące. Także kąt ścian ≥ 120° zwalnia z wymogu (§ 271 ust. 12 pkt 2). |
| Działka 10/2 i inne niezabudowane działki budowlane | wg MPZP | ≥ 4 m (połowa z 8 m) od granicy przy ścianie z > 65% części pełnej (§ 272 ust. 1); granica z działką drogową / placem publicznym – odległości z § 12 nie obowiązują (§ 12 ust. 10) |

---

## 12. Drogi pożarowe, dojścia, przejazdy (rozp. 2009) [O]

- **§ 12 ust. 1 pkt 1–2:** droga pożarowa wymagana do budynku z **ZL I** oraz do budynku **W** z ZL III → **wymagana**.
- **§ 12 ust. 2:** wzdłuż dłuższego boku na całej długości (przy krótszym boku > 60 m – z dwóch stron); **bliższa krawędź 5–15 m od ściany** (ZL); między drogą a ścianą **brak stałych elementów i drzew/krzewów > 3 m** utrudniających dostęp podnośników i drabin.
- **§ 12 ust. 3:** w uzasadnionych przypadkach (warunki lokalne, architektoniczne): dostęp do 30% obwodu (rozpiętość ≤ 60 m), 50% (> 60 m) albo **100% długości elewacji frontowej przy zabudowie pierzejowej** – przy spełnieniu pozostałych wymagań ust. 2.
- **§ 12 ust. 4:** wyjścia z budynku połączone z drogą **dojściem ≥ 1,5 m, ≤ 50 m**, z dotarciem do każdej strefy.
- **§ 12 ust. 5:** każdy dźwig ratowniczy – dojście ≤ 50 m (łącznie z drogą w budynku).
- **§ 12 ust. 9–11:** przejazd bez cofania lub **plac manewrowy 20 × 20 m** (albo inne rozwiązanie zawracania); odcinek „ślepy” do cofania ≤ 15 m; promień zewnętrzny łuku ≥ 11 m. **Uwaga:** przepis nie przewiduje odrębnego „placu manewrowego dla budynku wysokiego” – plac 20 × 20 m służy zawracaniu; ustawienie podnośnika zapewnia odcinek drogi z § 12 ust. 2 (4 m, ≤ 5%, 100 kN) (wniosek).
- **§ 12 ust. 12:** drogi i place bliżej niż 5 m od budynku (poza odcinkami z ust. 2–3) – jeśli ściana na tym odcinku i w odległości do 5 m ma klasę ściany oddzielenia.
- **§ 13 ust. 1–2:** szerokość **≥ 4 m**, spadek podłużny **≤ 5%** na odcinkach z § 12 ust. 2–3 (+10 m dojazdu); w mieście nacisk osi **100 kN**, poza tymi odcinkami szer. ≥ 3,5 m; **ust. 4** – rozwiązania zamienne za zgodą KW PSP.
- **§ 14:** przejazdy na dziedzińce: **wysokość ≥ 4,2 m, szerokość ≥ 3,6 m** (jezdnia ≥ 3 m), odległość między przejazdami ≤ 150 m.
- **§ 15:** elementy nad drogami pożarowymi (kładki, nadwieszenia, łączniki) – prześwit **≥ 4,5 m** (wys. i szer.).

**Zastosowanie do działki (wniosek):** drogami pożarowymi mogą być **ul. Mazowiecka** (zachód) i **Wybrzeże J. Słowackiego** (północ/wschód), jeżeli krawędź jezdni (lub utwardzonego pasa) jest 5–15 m od elewacji (pierzeja – § 12 ust. 3 pkt 3). Ryzyka: (1) **skwer od strony Wybrzeża Słowackiego** (teren użyczony Województwu, zieleń) – jeżeli elewacja wieży będzie > 15 m od jezdni, potrzebny utwardzony pas pożarowy w skwerze (np. płyty ażurowe/nawierzchnia wzmocniona pod 100 kN) i **bez drzew > 3 m** przed elewacją wieży; (2) ewentualna sieć trakcyjna/tramwajowa i drzewa uliczne mogą ograniczać pracę podnośnika – do weryfikacji; (3) **dojazd do wnętrza kwartału** (oznaczony na M.04) – jeżeli będzie przejazd pod budynkiem: 4,2 × 3,6 m (§ 14), lepiej 4,5 m (§ 15); (4) nadwieszenia bryły nad drogą pożarową – ≥ 4,5 m; (5) wejście dla PSP + dźwig ratowniczy + nasady 75 mm + hydranty zewnętrzne – od strony drogi pożarowej.

---

## 13. Interfejs: budowla ochronna / MDS (ochrona ludności) – flaga dla zespołu prawnego [O]
- **Art. 93 ust. 1 ustawy o ochronie ludności i obronie cywilnej** (brzmienie z Dz.U. 2026 poz. 646, w/ż 29.05.2026): **„W budynku użyteczności publicznej zapewnia się budowlę ochronną, chyba że przepis szczególny stanowi inaczej.”** Zwolnienie: decyzja wójta/burmistrza/prezydenta (ust. 2) [S16].
- **Rozp. MSWiA z 2.09.2026 (Dz.U. 2026 poz. 1181) § 2:** brak obowiązku m.in. gdy budynek **nie ma kondygnacji podziemnej i** ≤ 5000 m², gdy ≤ 50 os. (**z wyjątkiem siedziby organu administracji publicznej**), gdy budynek w rejestrze zabytków… → **nasz budynek nie spełnia przesłanek** (ma podziemie, > 5000 m², siedziba organu). § 3 – możliwe zwolnienie przez organ (np. budowla ochronna ≤ 500 m od wyjść, brak ekonomicznej zasadności, brak technicznych możliwości) [S17].
- **Art. 94:** gdy nie przewidziano budowli ochronnej – kondygnacje podziemne i garaże projektuje się tak, by umożliwić **MDS** o pojemności ≥ PU użyteczności publicznej / **15 m²/os.** (max 75% pow. netto / 1,5 m²/os.). **Art. 95a:** zawiadomienie wójta przed realizacją; organ określa pojemność i kategorię odporności (wyjątek ust. 6 pkt 1 dotyczy inwestorów: gmina, powiat, wojewoda – nie samorząd województwa; do weryfikacji). **Pb art. 33 ust. 2 pkt 13:** oświadczenie inwestora do wniosku o PnB.
- **Rozp. MSWiA z 9.07.2025 (Dz.U. 2025 poz. 932) – MDS:** § 6 – rozwiązania ewakuacyjne: 1 wyjście ewakuacyjne na każde rozpoczęte 200 os., 1 wyjście zapasowe na 400 os. (gdy > 30 os.), drogi ≥ 0,8 m, 0,4 m/100 os.; wyjście zapasowe **poza strefą zagruzowania = 1/3 wysokości budynku** (dla 45 m → 15 m); gdy niemożliwe – pojemność ≤ 300 os. i 2 klatki w odległości ≥ 15 m (lub szyb awaryjny); § 7 ust. 3 – część MDS w garażu **≥ 20 m od bramy garażowej** [S18].
- Program (11/2025) i F.15.A przewidują „parking podziemny pełniący funkcję MDS”. **Wniosek:** to może być niewystarczające po 29.05.2026 – w koncepcji pokazać garaż –2 z **rezerwą na ukrycie/schron** (strefa przy trzonach, ≥ 20 m od rampy, 2 niezależne wyjścia do klatek oddalonych ≥ 15 m, wentylacja filtrowentylacyjna w rezerwie) i opisać obie ścieżki (budowla ochronna albo zwolnienie + MDS wg art. 94). Szczegóły – osobne opracowanie (poza zakresem ppoż.).

---

## 14. Procedury i dokumenty
- **Uzgodnienie projektu (PZT, PAB, PT)** z rzeczoznawcą ds. zabezpieczeń ppoż. – art. 6b ustawy ppoż.; obowiązek dla naszego obiektu: rozp. 2023 § 3 ust. 1 **pkt 1** (strefa ZL I), **pkt 2** (W z ZL III), **pkt 6** (garaż wielokondygnacyjny) [S9][S14]; podstawa – „podstawowe dane dotyczące warunków ochrony ppoż.” i scenariusz pożarowy (definicja § 2 pkt 4 rozp. 2023).
- **Rozwiązania zamienne** – art. 6a ustawy ppoż.: postanowienie KW PSP na wniosek z ekspertyzą (np. atrium, wydłużone dojścia, nietypowe elewacje) [S9].
- **Odstępstwo** od przepisów techniczno-budowlanych – art. 9 Pb (zgoda organu a-b po upoważnieniu ministra; nie może ograniczać dostępności w obiektach użyteczności publicznej) [S7]. <!-- poprawione przez weryfikatora --> Wniosek do ministra musi zawierać m.in. (art. 9 ust. 3 pkt 4–5): dla obiektów na obszarach objętych ochroną konserwatorską (nasz teren – układ urbanistyczny w rejestrze zabytków) – **pozytywną opinię WKZ**; przy odstępstwie od przepisów bezpieczeństwa pożarowego – **ekspertyzę rzeczoznawcy ds. zabezpieczeń ppoż.** i postanowienie komendanta wojewódzkiego PSP o zgodzie na rozwiązania zamienne.
- **Oświadczenie inwestora z art. 102a Pb** (jeśli projekt wg WT 2002) – do wniosku, przed 20.03.2028 [S6].
- Regulamin: część opisowa ma zawierać **„założenia ochrony przeciwpożarowej”** (rozdz. o części opisowej) – propozycja tekstu w rozdz. 15.3.

---

## 15. Schemat ppoż. dla koncepcji – lista decyzji projektowych

### 15.1. Decyzje (do wdrożenia w modelu i na planszach) – wniosek
| # | Decyzja | Parametr / uzasadnienie |
|---|---|---|
| D1 | Budynek **W**, klasa odporności **„B”** | § 8, § 212; R 120 / REI 60 / EI 60 (o↔i) |
| D2 | **Strefy pożarowe = kondygnacje**, każda ≤ 2500 m² pow. wewnętrznej; większe dzielone ścianą REI 120 z drzwiami EI 60 | § 226 ust. 2, § 227, § 232 |
| D3 | Piętra Sejmiku (+ kancelaria) i strefa konferencyjna – **strefy ZL I**; biura – ZL III | § 209; dojścia 10/40 vs 30/60 m |
| D4 | **Trzony:** wieża – 2 klatki w oddzielnych trzonach (nie nożycowe) + dźwig ratowniczo-ewakuacyjny; każde skrzydło – klatka na końcu tak, by ślepe korytarze ≤ 20 m (ZL III) / ≤ 10 m (ZL I); dojścia przy 2 kierunkach ≤ 60 m / 40 m bez zwiększeń | § 246, § 256 |
| D5 | Klatki: bieg **1,6 m**, spocznik ≥ 1,6 m + **pole MOE 0,9 × 1,4 m** poza szerokością + wnęka na krzesło ewakuacyjne + EVCS; obudowa REI 60; biegi niepalne | § 68, § 249, M.13, Regulamin |
| D6 | **Przedsionki ppoż.** przed każdą klatką i dźwigiem ratowniczym na każdej kondygnacji (w tym podziemnych), ≥ 2,0 × 2,4 m (wózek), droga w przedsionku ≤ 5 m; drzwi EI 30 (korytarz) / E 30 (klatka) z napędami. <!-- poprawione przez weryfikatora --> Jeżeli dźwig ratowniczo-ewakuacyjny pełni też funkcję windy ogólnodostępnej: M.13 wymaga przed windą **≥ 3,6 m** między drzwiami windy a przeciwległą ścianą (pole 1,6 × 1,6 m + trasa 2 m) lub wnęki ≥ 2 m szer. z polem 1,6 × 1,6 m – przedsionek dźwigu projektować w tej głębokości | § 232 ust. 3–4, § 246, § 250 ust. 2; M.13 (rozdz. windy, pkt 6–7) |
| D7 | **Nadciśnienie** klatek, przedsionków i szybów dźwigów ratowniczych; **oddymianie korytarzy** wszystkich kondygnacji nadziemnych; szachty i wentylatory dachowe w modelu | § 246 ust. 2, § 247 ust. 1, § 253 ust. 4, § 270 |
| D8 | Dźwig ratowniczy (PN-EN 81-72) + ewakuacyjny (PN-EN 81-76) w wieży, szyb REI 60, zjazd do –2, wejście PSP ≤ 50 m od drogi pożarowej | § 253; rozp. 2009 § 12 ust. 5 |
| D9 | Ewakuacja przez hol główny – **tylko 1 klatka**; hol wys. ≥ 3,3 m, droga +50%, drzwi zewn. +50%; pozostałe klatki – wyjścia bezpośrednio na zewnątrz (ulica/podwórze) | § 256 ust. 6; odp. na pyt. 78 |
| D10 | Pustki: hol (parter+1) i foyer/galeria Sejmiku – suma połączonych kondygnacji ≤ 2500 m², oddymianie z sufitu; **bez atrium przez kondygnacje biurowe** | § 227, § 232 ust. 2, § 247 ust. 2 |
| D11 | **SSP + DSO** w całym budynku; **tryskacze** w całym budynku (rekomendacja); gaszenie gazem serwerowni i archiwum PZGiK | rozp. 2010 § 27–29 |
| D12 | Hydranty 25 przy trzonach na każdej kondygnacji, zawory 52 w przedsionkach (2/pion > 25 m i w podziemiu), piony DN 80 połączone na górze, zbiornik 25–100 m³ + pompownia (odrębna strefa), nasada 75 mm na elewacji | rozp. 2010 § 19–25; WT § 212 ust. 9 |
| D13 | Elewacja: **A1/A2-s1,d0** na całej wysokości, NRO, **pasy 0,8 m EI 60** (lub lamele/gzymsy ≥ 0,5 m EI 60), mocowania mechaniczne; ściany do sąsiadów > 65% części pełnej | § 216 ust. 2 i 8, § 223, § 225, § 271 |
| D14 | Styk z MZ19: **ściana oddzielenia REI 120**, pas 2 m EI 60 / wysunięcie 0,3 m, brak okien nad dachem MZ19 do +10 m w pasie 8 m (wniosek z § 218 – <!-- poprawione przez weryfikatora --> alternatywnie dach MZ19 w pasie 8 m NRO/R 30/RE 30, co wymaga ingerencji u sąsiada); rezerwa na przyszłe przejścia z drzwiami EI 60 (≤ 15% pow. ściany) | § 235, § 272 ust. 3, § 218, § 232 ust. 2; Wyjaśnienia nr 3 pyt. 13 |
| D15 | WS5: odsunięcie ≥ 8 m (przy > 65% części pełnej naszej ściany) lub ściana oddzielenia bez otworów; z tryskaczami ≥ 6 m | § 271 ust. 1, 4–7, 12 |
| D16 | Dachy: stropodach żelbetowy (REI 60), przekrycie BROOF(t1), dachy zielone z pasami żwiru; dachy skrzydeł w pasie 8 m od ścian wieży z oknami – NRO | § 216, § 218, § 219 |
| D17 | Garaż –1/–2: strefy ≤ 5000 m², oddymianie (SSP), hydranty 33, 2 wyjścia/strefę (≤ 40 m), przedsionki EI 30 do trzonów, pochylnia ≤ 20% wewnątrz/pod dachem (<!-- poprawione przez weryfikatora --> ≤ 15% na zewnątrz **bez** przekrycia; § 70 – garaż 1–2-poziomowy), wrota ≥ 1,5 m od okien | § 70, § 102–103, § 277–281 |
| D18 | **Drogi pożarowe**: Mazowiecka i Wybrzeże Słowackiego wzdłuż 100% elewacji frontowej (5–15 m od lica, 4 m, ≤ 5%, 100 kN, bez drzew > 3 m przed elewacją); 2 hydranty zewnętrzne DN 80 (≤ 75 m, ≥ 5 m od ściany) | rozp. 2009 § 5, § 10, § 12–15 |
| D19 | Centrum bezpieczeństwa przy wejściu głównym (SSP, DSO, EVCS, panel PSP, wyłączniki ppoż./PV/BESS) | § 183 WT; Regulamin (interkom) |
| D20 | Technika: trafostacja, rozdzielnie, agregat, BESS na parterze/–1 z dostępem z zewnątrz, odrębne strefy; **BESS nie wyżej niż 25 m** | § 182, § 212 ust. 8–9; projekt WT § 312 |
| D21 | Rezerwa OC: strefa ukrycia/MDS w garażu –2 (≥ 20 m od bramy, 2 wyjścia do klatek ≥ 15 m od siebie) | ustawa o ochronie ludności art. 93–94; rozp. 2025 poz. 932 |

### 15.2. Co pokazać na planszach (wniosek)
- Na rzutach (1:200): granice stref pożarowych (linia czerwona), kategorie ZL, klatki z przedsionkami (symbol nadciśnienia), dźwig ratowniczy „DR/FF”, pola MOE z piktogramem wózka i interkomu, hydranty, wyjścia ewakuacyjne i kierunki ewakuacji, długości dojść dla najdalszych punktów (kontrolnie).
- Na planie zagospodarowania (1:500): drogi pożarowe (kreskowanie), odległości 5–15 m, hydranty zewnętrzne, wejście dla PSP, dojście ≤ 50 m do dźwigu, strefa wolna od drzew > 3 m, odległości ppoż. do MZ19/WS5.
- Na przekroju: ściana oddzielenia przy MZ19, pasy międzykondygnacyjne, poziom 25 m (granica okładzin niepalnych / § 253), garaż i strefa OC.
- **Mały schemat ppoż.** (axo trzonów i stref) – dobrze ocenia się czytelność i dojrzałość projektu; łączyć z planszą dostępności (Regulamin wymaga rozwiązań dostępności – MOE to wspólny element).

### 15.3. Propozycja tekstu „Założenia ochrony przeciwpożarowej” do części opisowej (ok. 1/2 strony)
> Budynek zaprojektowano jako **wysoki (W)** w klasie odporności pożarowej **„B”**. Części biurowe stanowią strefy **ZL III**, sala obrad Sejmiku z zapleczem oraz strefa konferencyjna – odrębne strefy **ZL I**; garaż podziemny i pomieszczenia techniczne – strefy **PM**. Każda kondygnacja jest odrębną strefą pożarową o powierzchni nieprzekraczającej 2500 m². Ewakuację zapewniają **dwie niezależne klatki schodowe w wieży** oraz klatki w skrzydłach – wszystkie obudowane, poprzedzone **przedsionkami przeciwpożarowymi** i chronione **systemem nadciśnienia**; poziome drogi ewakuacyjne objęto **oddymianiem**. Na podestach klatek przewidziano **miejsca oczekiwania na ewakuację** dla osób na wózkach (poza wymaganą szerokością biegu), miejsca na krzesła ewakuacyjne i **dwustronną łączność głosową** z ochroną i stanowiskiem kierującego działaniem ratowniczym; w wieży – **dźwig dla ekip ratowniczych** przystosowany do ewakuacji osób z niepełnosprawnościami. Budynek wyposażono w **SSP, DSO, instalację tryskaczową**, hydranty wewnętrzne i zawory 52 na pionach nawodnionych, oświetlenie awaryjne i przeciwpożarowy wyłącznik prądu. Elewacje wykonano z **materiałów niepalnych** (A1/A2-s1,d0), z pasami międzykondygnacyjnymi EI 60; od strony kamienicy Mazowiecka 19 zastosowano ścianę oddzielenia przeciwpożarowego REI 120. Dostęp jednostek PSP zapewniają **drogi pożarowe** wzdłuż ul. Mazowieckiej i Wybrzeża J. Słowackiego oraz hydranty zewnętrzne. Rozwiązania spełniają przepisy techniczno-budowlane (WT 2002 – stosowane przejściowo na podstawie art. 102a Prawa budowlanego) oraz wymagania projektu nowych warunków technicznych.

---

## 16. Typowe błędy konkursowe w zakresie ppoż. (lista kontrolna)
1. **Atrium przez całą wysokość** biurowca W „na wizualizacji” – strefa > 2500 m² bez zgody na rozwiązania zamienne; brak pasów w ścianach atrium.
2. **Jedna klatka w wieży** („bo kondygnacja < 750 m²”) przy sali dla > 100 osób na ostatnim piętrze.
3. **Brak przedsionków** albo przedsionki 1,4 × 1,4 m, w których nie mieści się wózek z opiekunem; drzwi przedsionka kolidujące z biegiem.
4. MOE „na spoczniku” **zawężające** wymaganą szerokość (wprost zakazane w Regulaminie).
5. **Brak szachtów** nadciśnienia/oddymiania i wentylatorów na dachu → po urealnieniu trzony rosną o 10–20% (utrata powierzchni użytkowej i zaufania sądu do bilansów).
6. Pominięcie **dźwigu dla ekip ratowniczych** lub dźwig bez przedsionka; wejście PSP daleko od drogi pożarowej (> 50 m).
7. Ewakuacja **dwóch klatek przez jeden hol** (dopuszczalna tylko jedna – § 256 ust. 6).
8. Ślepe korytarze 30–40 m na piętrach Sejmiku (ZL I – limit 10 m).
9. **Pełne przeszklenie** elewacji bez pasów EI 60 i bez kotwienia okładzin; drewno/HPL/kompozyty powyżej 25 m; BIPV jako okładzina wieży.
10. **Okna w ścianie na styku z MZ19** albo nad jej dachem; przeszklona ściana zwrócona do WS5 w odległości < 8–16 m.
11. Skwer z alejami drzew **między jezdnią a elewacją** wieży, elewacja > 15 m od drogi; nadwieszenia < 4,5 m nad dojazdami; brak hydrantów zewnętrznych na planie.
12. Drzwi obrotowe jako jedyne wyjście z holu; drzwi wejściowe otwierane do środka; drzwi węższe niż bieg schodów.
13. Garaż: rampa > 20% (lub 15% bez przekrycia), brak drugiego wyjścia, wrota pod oknami biur, brak przedsionka do klatki; magazyn energii w garażu bez dostępu z zewnątrz.
14. Pomieszczenia **ZL w podziemiu** bez wydzielenia REI 120 → zmiana klasyfikacji wysokościowej (§ 212 ust. 5).
15. Schody „reprezentacyjne” w holu liczone jako droga ewakuacyjna z pięter wyższych.
16. Brak przeciwpożarowego wyłącznika prądu, centrum bezpieczeństwa i miejsca dla zbiornika/pompowni ppoż. w bilansie powierzchni.
17. Taras na dachu dostępny dla publiczności bez dwóch dróg ewakuacyjnych.
18. Opis „zgodnie z obowiązującymi przepisami” bez wskazania kategorii, klasy, stref i systemów – sąd i eksperci (Etap II) oczekują konkretów; Regulamin wymaga osobnego punktu „założenia ochrony przeciwpożarowej”.
19. Powoływanie się wyłącznie na WT 2002 jako „obowiązujące” – na 16.11.2026 to przepisy **stosowane przejściowo**; warto wykazać świadomość art. 102a Pb i projektu nowych WT.
20. Pominięcie obowiązków **ochrony ludności** (budowla ochronna / MDS) wpływających na garaż i trzony.

---

## 17. Kwestie otwarte / do weryfikacji
1. Czy po 16.11.2026 zostaną ogłoszone nowe WT i w jakim brzmieniu (wersja z 6.08.2026 wg źródła wtórnego) – monitorować ELI/ISAP (`api.sejm.gov.pl/eli/acts/search?publisher=DU&year=2026&title=warunków technicznych`).
2. Wydajność sieci wodociągowej (10/15/20 dm³/s) – MPWiK Wrocław → wielkość zbiornika ppoż. (25/50/100 m³).
3. Odległość jezdni Mazowieckiej i Wybrzeża Słowackiego od projektowanej elewacji; sieć trakcyjna, drzewa uliczne, nośność – dostęp podnośnika.
4. Udział części pełnej ściany szczytowej WS5 (M.08) i jej klasa – do ustalenia odległości z § 271.
5. Fundamenty i stan ściany szczytowej MZ19 (M.07) – możliwość wykonania ściany oddzielenia na własnym fundamencie; termin likwidacji okien MZ19.
6. Przyjęcie interpretacji: oddymianie korytarzy (§ 247) jako podstawa zwiększenia dojść (§ 256 ust. 4 pkt 2); wspólny przedsionek klatki i dźwigu ratowniczego.
7. Obowiązek budowli ochronnej (art. 93) vs MDS z programu – wymaga stanowiska Inwestora/organu ochrony ludności.
8. Treść wytycznych CNBOP-PIB/KG PSP dot. ładowania EV w garażach (status i wersja).
9. Aktualna edycja PN-EN 81-72 i stosowanie PN-EN 12101-13 zamiast PN-EN 12101-6 – w porozumieniu z rzeczoznawcą (WT przywołuje PN-EN 81-72:2005).

---

## 18. Źródła

### Oficjalne (pierwotne)
- **[S1]** Rozp. MI z 12.04.2002 (WT 2002), Dz.U. 2002 nr 75 poz. 690 – metryka i status (uznany za uchylony; uchylenie wynikające z Dz.U. 2019 poz. 1696, data 2026-09-21): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20020750690 ; https://api.sejm.gov.pl/eli/acts/DU/2002/690
- **[S2]** WT 2002 – t.j. Dz.U. 2022 poz. 1225: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20220001225 ; tekst: https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf
- **[S3]** Rozp. MRiT z 27.10.2023 zm. WT, Dz.U. 2023 poz. 2442: https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf
- **[S4]** Rozp. MRiT z 27.03.2024, Dz.U. 2024 poz. 474: https://api.sejm.gov.pl/eli/acts/DU/2024/474/text.pdf
- **[S5]** Rozp. MRiT z 9.05.2024 zm. WT, Dz.U. 2024 poz. 726: https://api.sejm.gov.pl/eli/acts/DU/2024/726/text.pdf
- **[S6]** Ustawa z 31.07.2026 o zmianie ustawy o samorządach zawodowych architektów oraz inżynierów budownictwa oraz ustawy – Prawo budowlane, Dz.U. 2026 poz. 1161 (art. 102a–102c Pb): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001161 ; https://api.sejm.gov.pl/eli/acts/DU/2026/1161/text.pdf
- **[S7]** Prawo budowlane – t.j. Dz.U. 2026 poz. 524 (art. 5, 7, 9, 29, 33): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000524 ; https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf
- **[S8]** Ustawa o zapewnianiu dostępności osobom ze szczególnymi potrzebami – t.j. Dz.U. 2024 poz. 1411 (art. 6 pkt 1 lit. e; art. 66): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20240001411
- **[S9]** Ustawa o ochronie przeciwpożarowej – t.j. Dz.U. 2025 poz. 188 (art. 6a–6f): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20250000188 ; https://api.sejm.gov.pl/eli/acts/DU/2025/188/text.pdf
- **[S10]** Rozp. MSWiA z 7.06.2010 w sprawie ochrony przeciwpożarowej budynków… – t.j. Dz.U. 2023 poz. 822: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20230000822 ; https://api.sejm.gov.pl/eli/acts/DU/2023/822/text.pdf
- **[S11]** Rozp. MSWiA z 21.11.2024, Dz.U. 2024 poz. 1716: https://api.sejm.gov.pl/eli/acts/DU/2024/1716/text.pdf
- **[S12]** Rozp. MSWiA z 28.09.2026, Dz.U. 2026 poz. 1276: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001276 ; https://api.sejm.gov.pl/eli/acts/DU/2026/1276/text.pdf
- **[S13]** Rozp. MSWiA z 24.07.2009 w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych, Dz.U. 2009 nr 124 poz. 1030: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20091241030 ; https://api.sejm.gov.pl/eli/acts/DU/2009/1030/text.pdf
- **[S14]** Rozp. MSWiA z 5.08.2023 w sprawie uzgadniania projektu… pod względem ochrony ppoż., Dz.U. 2023 poz. 1563: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20230001563 ; https://api.sejm.gov.pl/eli/acts/DU/2023/1563/text.pdf
- **[S15]** Projekt rozp. MFiG w sprawie warunków technicznych… (projekt z 24.04.2026) – tekst udostępniony w uzgodnieniach z KWRiST (repozytorium ZPP): https://zpp.pl/storage/library/2026-04/02499082537996b80db5bc355cbacf41.pdf ; OSR (11.05.2026): https://www.zpp.pl/storage/library/2026-05/8d1bd1626c8d81eaff8b6f595657919d.pdf ; uzasadnienie: https://www.zpp.pl/storage/library/2026-05/958496c9b3843165e763258b21b13910.pdf ; strona RCL (wg źródła wtórnego): https://legislacja.gov.pl/projekt/12398903 (16.11.2026: HTTP 503)
- **[S16]** Ustawa z 17.04.2026 o zmianie ustawy o ochronie ludności i obronie cywilnej oraz niektórych innych ustaw, Dz.U. 2026 poz. 646 (art. 93–95a): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000646 ; https://api.sejm.gov.pl/eli/acts/DU/2026/646/text.pdf
- **[S17]** Rozp. MSWiA z 2.09.2026 w sprawie zwalniania z obowiązku zapewniania budowli ochronnych…, Dz.U. 2026 poz. 1181: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001181 ; https://api.sejm.gov.pl/eli/acts/DU/2026/1181/text.pdf
- **[S18]** Rozp. MSWiA z 9.07.2025 w sprawie warunków organizowania oraz wymagań, jakie powinny spełniać miejsca doraźnego schronienia, Dz.U. 2025 poz. 932: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20250000932 ; https://api.sejm.gov.pl/eli/acts/DU/2025/932/text.pdf
- **[S19]** Rozp. MSWiA z 4.11.2025 w sprawie warunków technicznych dla budowli ochronnych…, Dz.U. 2025 poz. 1548 (sprawdzono tylko tytuł i status): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20250001548
- **[S20]** Materiały Organizatora (lokalnie): `00_materialy/tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt` (rozdz. „Dostępność”, „Część opisowa”), `Program_użytkowy_budynku_administracyjnego_UWMD_zatwierdzony_11_2025.txt` (s. 3, 4–5, 11–13, 15), `1089_Wyjasnienia_tresci_Regulaminu_nr_03/08/20-sig.txt` (pyt. 10, 13, 57, 78), `M.13._STANDARDY_DOSTĘPNOŚCI.txt` (szerokość biegu 1,6 m, ewakuacja), `Mapa schematyczna WRO UMWD - M.04.pdf`.

### Wtórne (pomocniczo)
- **[W1]** *Warunki techniczne 2026: nowe WT nie weszły. Co obowiązuje?* (stan na 14.10.2026): https://domy.energetycznyprojekt.pl/warunki-techniczne-2026/
- **[W2]** *Stare i nowe warunki techniczne dla budynków* (oprawiebudowlanym.pl, 2026): https://oprawiebudowlanym.pl/2026/07/stare-i-nowe-warunki-techniczne-dla-budynkow.html
- **[W3]** Wzmianka o „Wytycznych w zakresie ochrony przeciwpożarowej garaży… do ładowania samochodów elektrycznych i hybrydowych plug-in” (CNBOP-PIB/KG PSP/PSPA) – wynik wyszukiwania, treść niezweryfikowana; m.in. https://bip.um.wroc.pl/attachments/download/141255

### Pominięte
- Źródła o pracach nagrodzonych/konkurencyjnych w tym konkursie – **nie wyszukiwano i nie napotkano**.
- Niedostępne technicznie (16.11.2026): legislacja.gov.pl (HTTP 503), technical-regulation-information-system.ec.europa.eu – notyfikacja nowych WT (HTTP 401), izolacje.com.pl – artykuł o WT 2026 („brak dostępu”).

---

## 19. Weryfikacja adwersaryjna (16.11.2026) <!-- poprawione przez weryfikatora -->

Weryfikator pobrał teksty aktów z API ELI Sejmu (`api.sejm.gov.pl/eli/acts/DU/…/text.pdf`) i porównał z dokumentem. Nie korzystano ze źródeł o pracach konkursowych.

**Potwierdzone w tekście źródłowym (POPRAWNE):** status WT 2002 i podstawa uchylenia (ELI: DU/2002/690, repealDate 2026-09-21, „Uchylenia wynikające z” DU/2019/1696); brzmienie art. 102a–102c Pb i w/ż art. 2 pkt 4 ustawy Dz.U. 2026 poz. 1161 (2.09.2026); brak nowych WT dla budynków w Dz.U. do poz. 1497 z 13.11.2026; WT 2002 (t.j. 2022 poz. 1225): § 6, § 8 pkt 3, § 68 ust. 1–2, § 69, § 70, § 102, § 103, § 181 ust. 1, 3, 5, § 182, § 183 ust. 2–4, § 187 ust. 3, 5, 7, § 193 ust. 4, § 208a ust. 3, § 209, § 210, § 212 ust. 2, 4, 5, 7–9, § 214, § 216 ust. 1 (tabela kl. „B”), 2, 7, 8, § 218, § 219, § 220, § 223, § 224, § 225, § 226, § 227 ust. 1–4, § 228, § 232 ust. 2–4, 6, § 235, § 236 ust. 4, 6, § 237, § 238, § 239, § 240, § 241, § 242, § 243, § 244, § 245, § 246, § 247, § 249, § 250, § 251, § 252, § 253, § 256 ust. 1–7 (tabela dojść), § 258–262, § 268, § 270, § 271, § 272, § 275, § 277–281, § 292, zał. 1 (PN-EN 81-72:2005, PN-B-02867:2013), zał. 3 pkt 4 (BROOF(t1)); rozp. MSWiA 2010 (t.j. 2023 poz. 822 + 2024 poz. 1716 + 2026 poz. 1276): § 19–25, § 27–29; rozp. MSWiA 2009 (Dz.U. 2009 nr 124 poz. 1030): § 5 ust. 1 pkt 2, § 7 ust. 1, § 10 ust. 6 i 8, § 12, § 13, § 14, § 15; rozp. MSWiA 2023 poz. 1563 § 3 ust. 1 pkt 1, 2, 6 (oraz pkt 7 – obiekty z SSP/DSO); ustawa o ochronie ppoż. art. 6a–6b; Pb art. 9, art. 29 ust. 4 pkt 3 lit. c, art. 33 ust. 2 pkt 13 (brzmienie z Dz.U. 2026 poz. 646); ustawa o dostępności art. 6 pkt 1 lit. e i art. 66; ustawa o ochronie ludności art. 93, 94, 95a (brzmienie z Dz.U. 2026 poz. 646); rozp. Dz.U. 2026 poz. 1181 § 2–3; rozp. Dz.U. 2025 poz. 932 § 6, § 7 ust. 3; projekt WT z 24.04.2026: § 8, § 227 ust. 9–10, § 234 ust. 1–4, § 252, § 253, § 258, § 267, § 310–312, § 393; Regulamin (MOE, interkom, „założenia ochrony przeciwpożarowej”), Wyjaśnienia nr 3 (pyt. 13), nr 8 (pyt. 57), nr 20 (pyt. 78); M.13 (bieg 1,6 m).

**Poprawione:** (1) w/ż Dz.U. 2023 poz. 2442 – 1.08.2024 (nie 1.04.2024); (2) D17 – pochylnia 15% dotyczy pochylni zewnętrznej **bez** przekrycia; (3) tryskacze nie zmniejszają łącznej ilości wody (rozp. 2009 § 7 ust. 1 pkt 2); (4) § 218 – wymaganie dotyczy dachu niższego budynku (MZ19), „brak okien” to wniosek; (5) zakres zmian 2024 poz. 726 i 2024 poz. 1716; (6) Dz.U. 2025 poz. 1705 w/ż 1.01.2027; (7) charakter odesłań w rozp. MSWiA 2009/2010 do WT 2002 – niepewny, nie „statyczny”. **Dopisane:** § 228 ust. 2 (PM w podziemiu 50%), art. 9 ust. 3 pkt 4–5 Pb (opinia WKZ, ekspertyza ppoż.), M.13 – przestrzeń 3,6 m przed windą, uwaga do § 239 ust. 4, rozbieżność daty utraty mocy WT 2002 (ISAP 21.09 vs art. 102a „do 19.09”).

**Niezweryfikowane (NIEPEWNE):** treść OSR/uzasadnienia projektu WT i wersja z 6.08.2026 (RCL niedostępne); pozostałe paragrafy projektu WT przywołane w tabeli 2.3 (§ 221, 239, 247, 260, 261, 268, 287, 289, 303–304) sprawdzone wyrywkowo (§ 239, § 234 – zgodne); parametry normowe PN-EN 81-72/81-76 i BS 9999 (normy, nie przepisy).
