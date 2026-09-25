# `lamela.draft` — silnik rysunkowy dokumentacji budowlanej

Programowe generowanie rysunków w standardzie polskiej dokumentacji projektowej (PZT, rzuty, przekroje, elewacje,
detale, konstrukcja, instalacje) z modelu danych w **metrach**, z wyjściem:

* **DXF R2018** — przestrzeń modelu w metrach (`$INSUNITS = 6`) + arkusz (layout) w mm z rzutniami `VIEWPORT`
  w dokładnej podziałce; polskie nazwy warstw z grubością, rodzajem linii, kolorem i opisem; napisy UTF-8 w stylu
  TrueType Arial (Liberation Sans jest z nim metrycznie zgodna — układ napisów w CAD = PDF),
* **PDF wektorowy** w dokładnej skali (strona = format arkusza, 1 mm = 72/25,4 pt; czcionki osadzone,
  napisy wyszukiwalne, polskie znaki),
* **PNG** podglądowy (rasteryzacja PDF przez PyMuPDF, domyślnie 200 dpi, metadane dpi),
* **tom PDF** (wiele arkuszy różnych formatów + spis rysunków).

Uruchomienie: `PYTHONPATH=src python3 …`. Zależności: ezdxf ≥ 1.4, matplotlib, shapely ≥ 2.1, numpy, pymupdf,
Pillow. Demonstracja i test: `PYTHONPATH=src python3 tools/draft_demo.py` → `projekt/00_demo_silnika/`.

Reguły norm pochodzą z PN-EN ISO 5457, 7200, 128-2/-3, 3098, 5455, PN-B-01025/-01027/-01029/-01030,
PN-EN ISO 4157, IEC 60617 oraz ze specyfikacji `docs/10_podstawy_prawne/R4_rysunek_budowlany_normy.md` (R4) —
wartości „[przyjęcie]” z R4 są w silniku domyślne; odstępstwa silnika opisano niżej (sekcja *Zgodność z R4*).

---

## 1. Model pojęciowy

```
model [m] ──(Viewport: 1:scale, k = scale/1000 m na 1 mm papieru)──► arkusz [mm] ──► DXF / PDF / PNG
```

* **`Canvas`** — wspólny interfejs rysowania: `line`, `polyline`, `polygon`, `rect`, `circle`, `arc`, `fill`,
  `text`, `geom` (shapely), `dot`. Wszystkie wielkości „papierowe” (wysokość pisma, rozstaw kreskowania, długość
  kreski ograniczającej, średnica kółka osi) podaje się w **mm papieru** i przelicza przez `c.k`
  (`c.mm(3.0)` = 3 mm na wydruku w jednostkach płótna). Dzięki temu każda funkcja symboli / wymiarów / kreskowań
  działa identycznie w rzutni (metry) i na arkuszu (mm).
* **`Sheet`** (płótno arkusza, k = 1) — format, ramka, tabliczka, rzutnie, zapis.
* **`Viewport`** (płótno modelu, k = scale/1000) — treść w metrach; `sheet.place(vp, x, y, anchor)` dopasowuje
  okno rzutni do zawartości (lub do `clip_model`), `vp.to_sheet(pts)` / `vp.to_model(pts)`.
* **Prymitywy**: `PLine`, `PArc`, `PFill`, `PText` (napis z przebiegami — np. wymiar 24⁵ = „24” + indeks „5”).
  Każdy ma warstwę, pióro (rola lub mm), rodzaj linii, kolor, `z` (kolejność rysowania).
* **Pióra** — rola (`'b_cienka'`, `'cienka'`, `'srednia'`, `'gruba'`, `'b_gruba'`) rozwiązywana wg grupy linii
  podziałki rzutni albo grubość jawna w mm (szereg ISO 128-2).

## 2. Szybki start

```python
from lamela.draft import Sheet, TitleBlock, Osoba, dims, symbols as S, hatch, elements as E, plot

tb = TitleBlock(pracownia="…", inwestor="…", obiekt="Budynek mieszkalny jednorodzinny „Dom LAMELA”",
                lokalizacja="dz. nr 123/4, obręb 0005 Przykładowo", kategoria="I", stadium="PB",
                branza="ARCHITEKTURA (AR)", tytul="RZUT PARTERU", skala="1:50", nr_rysunku="PB-AR-01",
                data="2026-09-25", arkusz="1/12", rodzaj="rzut", rewizja="0")
sh = Sheet("A3", title_block=tb)                  # ramka 20/10 mm, znaki składania i centrujące, tabliczka
vp = sh.add_viewport(50, "RZUT PARTERU")          # rzutnia 1:50 — rysujemy w METRACH

cs = E.CutSet()                                   # ściany warstwowe (od wnętrza do zewnątrz)
E.ring_layers(cs, [(0, 0), (7.2, 0), (7.2, 5.7), (0, 5.7)],
              [("TYNK", .015, "wyk"), ("MUR_SILIKAT", .18, "konstr"), ("IZOL_TWARDA", .20, "izol"), ("TYNK", .007, "wyk")])
cs.cut_out(E.opening_rect((0, 0), (7.2, 0), 1.3, 2.2))       # otwór okienny
cs.draw(vp)                                                   # kreskowanie PN-B-01030 + kontury wg rodzaju
S.window(vp, (1.3, 0), (2.2, 0), s_int=0.105, s_ext=-0.297, frame_in=-0.03, frame_out=-0.115)
dims.dim_h(vp, [-0.29, 1.3, 2.2, 7.49], y=-0.79, y_ref=-0.29)                 # łańcuch wymiarowy
dims.opening_dim(vp, (1.75, 0.105), (1, 0), 0.90, 1.50, sill=0.85, symbol="O1")
S.room_tag(vp, (3.0, 2.5), "1.01", "Pokój", 18.61, level_z=0.0)
S.axis_line(vp, (0, -2.4), (0, 6.6), "A")

sh.place(vp, sh.frame[0] + 5, sh.frame[3] - 5, "tl")           # dopasowanie rzutni do zawartości
sh.view_title(vp)                                                # „RZUT PARTERU 1:50”
hatch.legend(sh, 240, 200, ["MUR_SILIKAT", "IZOL_TWARDA", "TYNK"])  # legenda generowana z kodów
files = sh.save("projekt/…/PB-AR-01")          # {'pdf':…, 'png':…, 'dxf':…}
print(plot.qa(sh))                               # kontrola wg R4 pkt 3.14
```

## 3. API — moduły i najważniejsze funkcje

### `sheet` — arkusze (PN-EN ISO 5457, 7200, 9431)
| Funkcja / klasa | Opis |
|---|---|
| `sheet_size(fmt, orientation=None) -> (W, H)` | A0–A4, wydłużone `A3x3`, `A2×3`, ogólnie `Ak×n` (A4 pionowo, reszta poziomo); niestandardowe `"780x594"` (szer. × wys., jak zapisano; `custom_size`) |
| `fold_positions(W, H) -> (xs, ys)` | linie składania do A4 „do wpięcia” (praktyka DIN 824 forma A, uogólniona na formaty wydłużone i niestandardowe): harmonijka o nieparzystej liczbie pasów ≤ 210 mm (rodzina A: 210 + pary równe; rodzina B: (20 + m) + m… + 190 — wariant o najlepszej ocenie), pierwszy pas z marginesem 20 mm, pas z tabliczką ≥ 190 mm na wierzchu; potem co 297 mm od dołu — `lamela.draft.skladanie` |
| `skladanie.pasy_pionowe(W)`, `warianty_pasow(W)`, `rzedy_poziome(H)`, `ocena_pionowa(pasy, W)`, `ocena_skladania(W, H, tb_h=None)`, `opis_skladania(W, H)` | pasy harmonijki, rzędy, plan i ocena „dobre/poprawne/słabe” (progi jak `tools/metryki_arkuszy.py`) + warunek „tabliczka na wierzchu” |
| `Sheet(fmt="A3", orientation=None, title_block=None, binding=20, margin=10, fold_marks=True, centring_marks=True, grid_reference=None, draw_frame=True)` | ramka 0,7 mm; znaki centrujące 0,7 mm do 10 mm za ramkę; siatka odniesień 50 mm od osi symetrii (litery bez I/O, 3,5 mm, 0,35 mm — domyślnie dla ≥ A2); oznaczenie formatu w dolnym marginesie; znaki składania z numerami kolejności zgięć (1,8 mm, przy krawędzi arkusza); format niestandardowy: `Sheet("780x594")` (`sh.custom`, opis na marginesie „nst. 780×594”); `centring_marks={strona: mm}` — krótsze wejście znaku za ramkę |
| `sh.przytnij_znaki_centrujace(odstep=1.5, min_gl=2)` | po narysowaniu treści: znak centrujący (ISO 5457 4.3: 0,7 mm, zalecane 10 mm za ramką; kształt dowolny) kończy się `odstep` przed treścią (prymitywy arkusza i rzutni), wejście < `min_gl` — na ramce; zwraca `{g, d, l, p: mm}` (`sh.znaki`, `sh.znaki_gl`); `znaki_centrujace(W, H, frame)` — geometria znaków |
| `Sheet.add_viewport(scale, title, subtitle=None) -> Viewport` | nowa rzutnia |
| `Sheet.place(vp, x, y, anchor="tl", pad=3.0, clip_model=None)` | umieszczenie rzutni (kotwica `tl/tr/bl/br/mc…`) |
| `Sheet.view_title(vp, text=None, scale=True, where="below"|"above", dx, dy, h=5.0)` | tytuł widoku z podziałką i podkreśleniem (dla przekrojów `where="above"` — ISO 128-3) |
| `Sheet.free_above_title_block() -> rect` | pole tekstowe nad tabliczką |
| `Sheet.save(base, formats=("dxf","pdf","png"), dpi=200, mode="branze", dxf_mode="layout")` | zapis |
| `TitleBlock(...)`, `Osoba(funkcja, imie_nazwisko="", specjalnosc_uprawnienia="", data="")` | pola: pracownia, adres pracowni, inwestor, obiekt, lokalizacja (działka/obręb/jedn. ewid.), kategoria, stadium, branża, tytuł, skala, nr rysunku, format (auto), data wydania, rewizja, **arkusz**, **rodzaj dokumentu**, `sprawdzenie` (False — bez wiersza „Sprawdzający”), `osoby` (Projektant / Projektant (wsp.) / Sprawdzający / Opracował — pola PUSTE do ręcznego uzupełnienia, kolumna PODPIS zawsze pusta), `rewizje` (tabela zmian nad tabliczką) |
| `notes_box(sh, x, y_top, w, lines, title="UWAGI", h=2.5, start=1)` | uwagi numerowane, zawijane (`start` — numer pierwszej uwagi, ciąg dalszy bloku dzielonego) |
| `table(sh, x, y_top, cols, rows, h=2.5, row_h=5, title=None, align=None, zawijaj=False)` | zestawienia (pomieszczeń, stolarki…); tekst zmniejszany do 1,8 mm, `zawijaj=True` — dłuższy łamany w komórce (wiersz rośnie) zamiast wchodzić na sąsiednią kolumnę |
| `scale_bar(c, pos, scale, length_m=None, h=1.8)` | podziałka liniowa (ISO 5455) |
| `control_segment(sh, pos, length=100, vertical=False)` | odcinek kontrolny wydruku 1:1 |
| `lines_legend(c, x, y_top, entries=None, scales=(20,50,100,500))` | tabela rodzajów i grubości linii wg grup |
| `lettering_sample(c, x, y_top, heights)` | próbka pisma z polskimi znakami |

### `styles` — warstwy, linie, pismo
* `LAYERS` — ~60 warstw z prefiksami branż: `R-` (arkusz), `A-` (architektura: `A-SCIANY-KONSTR`,
  `A-SCIANY-IZOL`, `A-SCIANY-WYK`, `A-STROPY`, `A-IZOL-WODNA`, `A-KRESKOWANIE`, `A-OKNA`, `A-DRZWI`, `A-SCHODY`,
  `A-MEBLE`, `A-SANITARNE`, `A-WYMIARY`, `A-OPISY`, `A-OSIE`, `A-RZEDNE`, `A-PRZEKROJE`, `A-NAD-CIECIEM`…),
  `K-` (`K-ZBROJENIE`…), `S-` (`S-WODA`, `S-CWU`, `S-CYRK`, `S-KANAL`, `S-WENT`…), `E-` (`E-GNIAZDA`,
  `E-OSWIETLENIE`, `E-LACZNIKI`…), `Z-` (PZT). Każda: opis, rola pióra, rodzaj linii, kolor ACI, kolor wydruku
  branżowego, `z`. `layer(name)` tworzy definicję domyślną dla nieznanej nazwy.
* `LINE_GROUPS`, `use_profile("R4"|"R4-scisly"|"lekki")`, `pen_mm(pen, scale, default_role, paper)`,
  `line_group_name(scale)` — grupy: 1:100 → 0,25/0,5/1,0 (symbole 0,35); 1:50 i detale → 0,35/0,7/1,4 (0,5);
  PZT → wg PN-B-01027; `b_cienka` (kreskowanie, meble) = stopień poniżej cienkiej (profil `R4-scisly` = cienka).
* `LINETYPES` — wzory wg ISO 128-2 (d = 0,35: kreska 12d, przerwa 3d, kreska długa 24d, kropka):
  `CIAGLA`, `KRESKOWA`, `KRESKOWA_DROBNA`, `PUNKTOWA`, `PUNKTOWA_KROTKA`, `DWUPUNKTOWA`, `KROPKOWA`,
  `KRESKA_DLUGA`, `KRESKOWA_3_1` (paroizolacja), `WIELOPUNKTOWA` (t), `KABEL_E` (e), `HYDRO_OKNA`.
* `TEXT_SERIES = (1.8, 2.5, 3.5, 5, 7, 10, 14, 20)`, `snap_text_h(h)`; czcionki `FONT_FILES`, `DXF_FONTS`.

### `fmt` — zapis liczb
`num(x, nd)` (przecinek, minus typograficzny), `dim_parts(m, unit="cm") -> ("24", "5")`, `dim_text`,
`level(z, nd=None)` → `±0,000 / +3,150 / −0,300` (`LEVEL_DECIMALS = 3`, PZT: `LEVEL_DECIMALS_PZT = 2`),
`level_abs`, `area(m2) -> "12,34 m²"`, `percent`, `scale_str`.

### `hatch` — materiały w przekroju (PN-B-01030 + oznaczenia przyjęte, R4 pkt 3.8)
* `hatch(c, shape, material, layer="A-KRESKOWANIE", outline=False, angle=None, spacing=None, axis=None, seed=None, band_mm="auto")`
  — geometria przycięta shapely; rozstawy w mm papieru; `axis=(p1,p2)` — kierunek warstwy (wężyk, zygzak, drewno);
  pola szersze niż 30 mm kreskowane pasem 5 mm przy brzegu.
* Kody (32): `ZELBET` (45° na przemian ciągłe/przerywane 1,5 mm), `BETON` (45° przerywane 2 mm), `BETON_LEKKI`,
  `BETON_LEKKI_ZBROJONY`, `BETON_KOMORKOWY`, `MUR_CERAMIKA` (45° 1,5), `MUR_SILIKAT` (kratka 45°/135° 2 mm),
  `DREWNO_POPRZ`, `DREWNO_WZDL`, `SKLEJKA`, `PLYTA_DREWNOPOCHODNA`, `STAL` (zaczernienie; duże — 45° 0,7),
  `IZOL_MIEKKA` (meander, skok 2 mm), `IZOL_TWARDA` (zygzak 2 mm), `IZOL_XPS`, `IZOL_PIR`,
  `IZOL_PRZECIWWODNA` (pas czarny 3 / biały 1,5), `IZOL_PRZECIWWILGOCIOWA`, `PAROIZOLACJA` (kreskowa 3/1),
  `MEMBRANA_PAROPRZEP`, `SZKLO`, `TWORZYWO`, `TYNK`, `PLYTA_GK`, `JASTRYCH`, `PLYTKI`, `GRUNT_RODZIMY`,
  `NASYP`, `PIASEK`, `ZWIR`, `POSPOLKA`, `HUMUS`; aliasy (`resolve`): `EPS`, `WELNA`, `XPS`, `SILIKAT`, `GRES`…
  Kody zgodne z polem `kreskowanie` materiałów w `model/budynek.yaml`.
* `membrane(c, pts, kind)` — warstwy cienkie wzdłuż łamanej; `ground_line(c, pts)` — linia terenu z oznaczeniem
  gruntu; `ground_band(...)`; `legend(c, x, y_top, codes, cols, col_w, sw, h, title, show_source)` — legenda
  generowana automatycznie (nazwa + źródło oznaczenia); `PATTERNS`, `register(code, name, source, kind)` — własne wzory.

### `elements` — elementy przecięte
* `CutSet()`: `add(poly, mat, kind, priority=None, axis=None, angle=None, group=None)`, `cut_out(poly)`,
  `resolve()`, `draw(c, hatch=True, outlines=True, fill_konstr=None, merge_thin_mm=0.7, blacken_mm=1.5, black_gap_mm=0.7)`.
  Rodzaje: `konstr`, `strop`, `fund`, `dzial`, `izol`, `warstwa`, `wyk`, `membrana`, `grunt`, `stal` (pióro
  konturu i priorytet w `KIND_STYLE`). Reguły: nakładanie wg priorytetu, scalanie jednorodnego muru, warstwy
  < 0,7 mm na papierze dołączane do sąsiada o najdłuższej wspólnej krawędzi (R4-C04), przekroje konstrukcyjne
  < 1,5 mm zaczerniane z prześwitem 0,7 mm.
* `ring_layers(cs, axis_poly, layers)` — ściana zewnętrzna wzdłuż obrysu osi (narożniki na ucios, kawałki per
  krawędź), `wall_layers(cs, p1, p2, layers, justification="konstr"|"left"|"center"|"right", angle=None)`,
  `layer_offsets(layers)`, `opening_rect(p1, p2, a, b, depth=0.35)`,
  `section_h(cs, x0, x1, z_top, layers)` / `section_v(cs, z0, z1, x_start, layers, direction)` — przegrody w przekroju.

### `dims` — wymiarowanie (PN-B-01029) i rzędne (PN-B-01025)
| Funkcja | Opis |
|---|---|
| `dim_chain(c, pts, at, direction="h"|"v"|kąt, h=2.5, unit_="cm"|"mm"|"m", ext="short"|"full", labels=None, mask=0)` | łańcuch: kreski 45° dł. 3 mm, linia wymiarowa +2 mm, pomocnicze jednakowe (2 mm / 2 mm) lub od obiektu (odstęp 2 mm), liczby 1 mm nad linią, czytelne od dołu/prawej; indeks górny mm; automatyczne rozsuwanie kolizji (obok odcinka → pod linią → drugi poziom z odnośnikiem); rejestr `c.dim_chains` dla QA |
| `dim_h(c, xs, y, y_ref)`, `dim_v(c, ys, x, x_ref)`, `dim_aligned(c, p1, p2, offset_mm)` | skróty |
| `opening_dim(c, center, wall_dir, width, height, sill=None, side=1, symbol=None, axis_mm=14)` | ułamek na osi otworu `szer / (parapet) wys` + symbol stolarki w kółku (albo sam symbol: `width=height=None`) |
| `level_section(c, pt, z, kind="wyk"|"konstr"|"zero"|"pn", side, abs_z=None)` | rzędna na przekroju/elewacji: trójkąt zaczerniony / pusty / w połowie zaczerniony z rzędną bezwzględną pod linią / grot otwarty (PN) |
| `levels(c, x, [(z, kind[, abs_z]), …], side)` | kolumna rzędnych z automatycznym rozsuwaniem |
| `level_plan(c, pt, z, style="x"|"o"|"box")` | rzędna na rzucie („×”+linia odniesienia, kółko, ramka) |
| `slope(c, p_from, p_to, value_pct, ramp=False)` | spadek (grot w kierunku spadku) / pochylnia (kółko + grot) |
| `dim_radius`, `dim_angle`, `leader(c, pts, text, end="arrow"|"dot"|"none")`, `arrowhead`, `dim_runs` | pozostałe |

### `symbols` — symbole (re-eksportuje `symbols_inst` i `symbols_site`)
Konwencja: `pos` w jednostkach płótna, `rot` [°]; dla elementów przyściennych lokalna oś +y = „od ściany do
pomieszczenia”; wymiary rzeczywiste w m, symbole umowne w mm papieru (`s_mm`, `r_mm`, `size_mm`).

* Adnotacje: `north_arrow(c, pos, size_mm=16, north_deg=0)`, `axis_line(c, p1, p2, label, bubbles, r_mm=5)`,
  `axes_grid(c, xs, ys, bbox)`, `section_mark(c, p1, p2, label, look=±1)`, `detail_callout`, `room_tag(c, pos,
  number, name, area_m2, floor=None, level_z=None)` (numer i nazwa podkreślone), `layer_callout(c, p_start,
  p_end, texts, side, marks, title)` („drabinka”), `tag(c, pos, text, shape="circle"|"ellipse"|"hex"|"rect")`,
  `entrance_arrow`.
* Stolarka i komunikacja: `door(c, p_a, p_b, wall_t, side, hinge, leaves=1|2, style="arc"|"line30", threshold)`,
  `sliding_door(c, p_a, p_b, wall_t, side, kind="HS"|"chowane"|"naścienne", fixed)`, `window(c, p_a, p_b,
  s_int, s_ext, frame_in, frame_out, side, glass=2, sill_in, sill_out)`, `stairs(c, start, direction, width,
  n_steps, tread, riser, cut_after, first_no, total_steps, label_style="inline"|"fraction")`,
  `floor_opening(c, poly, kind="otwor"|"wneka")`, `duct(c, poly, kind="went"|"spalinowy"|"dymowy")`.
* Wyposażenie (skala rzeczywista): `wc_hung`, `washbasin`, `washbasin_counter`, `bathtub`, `shower_walkin`
  (odpływ liniowy, ścianka szklana, spadki), `washing_machine`, `dryer`, `kitchen_sink`, `hob`, `fridge`,
  `dishwasher`, `appliance`, `counter`, `bed`, `wardrobe`, `sofa`, `table_chairs`, `desk`, `kitchen_island`.
* Elektryka (IEC 60617, dawne 11-xx-xx): `socket(n, earth, ip44, phases)`, `switch(kind="1"|"2"|"swiecznikowy"|
  "schodowy"|"krzyzowy"|"przycisk")`, `light(kind="sufit"|"kinkiet"|"sciana"|"downlight"|"awaryjna")`,
  `light_linear`, `panel`, `junction_box`, `motion_sensor`, `bell`, `videophone`, `data_outlet(label="RJ45"|"TV")`,
  `earth`, `spd`.
* Sanitarne / HVAC: `pipe(c, pts, medium="WZ"|"WC"|"CYRK"|"KS"|"KD"|"Z"|"P"|"ODA"|"SUP"|"ETA"|"EHA", label)`,
  `media(code)`, `riser`, `valve`, `check_valve`, `water_meter`, `filter_`, `manifold`, `pump`, `tank`,
  `heat_pump`, `cleanout`, `floor_drain`, `inspection`, `grille`, `anemostat(kind="N"|"W")`,
  `air_terminal(kind="czerpnia"|"wyrzutnia")`, `recuperator` (ODA/EHA/ETA/SUP), `radiator`, `floor_heating`.
* Teren (PN-B-01027): `tree(existing, remove, conifer, transplant)`, `shrub`, `hedge(conifer)`, `lawn`,
  `paving(kind="drobne"|"duze"|"zwir"|"asfalt"|"deska")`, `retaining_wall`, `pole`, `hydrant`, `manhole`,
  `cable_box` (ZK), `utility_box` (SW/SG), `plot_boundary(corner_labels, coords)`, `boundary_line` (linia
  rozgraniczająca), `building_line(kind="nieprzekraczalna"|"obowiazujaca", side)`, `fence`,
  `utility_line(kind="woda"|"kan_sanit"|"kan_deszcz"|"gaz"|"energ"|"tele"|"cieplo", connection_end)`,
  `building_label(pos, zero_abs, "III")`, `site_entrance`, `contours(lines, projected)`, `spot_height`, `gate`.

### `render`, `dxfout`, `plot` — wyjście i kontrola
* `render.to_pdf(sheet, path, mode="branze"|"mono"|"screen")`, `render.pdf_to_png(pdf, png, dpi)`,
  `render.to_png`, `render.sheets_to_pdf(sheets, path)`, `render.build_figure(sheet)`.
* `dxfout.to_dxf(sheet, path, mode="layout"|"flat")` — layout: model w m + VIEWPORT (każda kolejna rzutnia
  przesunięta w modelu w prawo, adnotacje w skali własnej rzutni); rodzaje linii w mm z `ltscale = scale/1000`
  na encjach modelu (`PSLTSCALE = 0`); flat: wszystko w mm arkusza.
* `plot.volume(sheets, pdf, title, toc=True)` — tom ze spisem rysunków (`plot.spis_rysunkow`: nagłówek 5 / 3,5 mm
  łamany do szerokości pola, tytuły łamane w komórkach, pole spisu między znakami centrującymi);
  `plot.check_scale(pdf, sheet, vp, p1, p2)`
  — pomiar odcinka w PDF; `plot.pdf_segments(pdf)`; `plot.check_png(png, sheet, min_dpi=150)`;
  `plot.add_control_marks(sheet)`; `plot.qa(sheet, kind=None)` — kontrola R4 pkt 3.14 (metryka § 10, legenda,
  podziałki minimalne, grubości z szeregu ISO 128-2, pismo z szeregu ISO 3098 / ≥ 2,5 mm na PZT, sumy łańcuchów;
  ostrzeżenie o znakach spoza kroju pisma). Znaki spoza Liberation Sans z tablicy `text.ZAMIENNIKI` (⌀, ∅ → Ø)
  są zamieniane w pomiarze, PDF i DXF (`text.normalizuj`).

## 4. Zgodność z R4 i odstępstwa (przyjęcia silnika)
* Grupy linii R4 pkt 3.2 (0,5 przy 1:100, 0,7 przy 1:50/detalach); **kreskowanie i meble o stopień cieńsze**
  od linii cienkiej grupy (profil `R4-scisly` wyrównuje).
* Rzędne 3 miejsca (arch.-bud.), 2 na PZT (`fmt.LEVEL_DECIMALS`). Oprócz wariantu PN (`kind="pn"`, grot otwarty)
  dostępny wariant praktyki: trójkąt zaczerniony = wykończenie, pusty = konstrukcja (objaśniać w legendzie).
* Wymiary w cm z mm w indeksie górnym (praktyka, R4-F07 — objaśniać w uwagach arkusza).
* Kropki tynku/jastrychu ok. 25–35/cm² (R4 proponuje ok. 8/cm²) — dla czytelności wzoru z reprodukcji PN-B-01030.
* Szerokość pisma 1,0 (R4: „Arial CE, szer. 0,8” — źródło wtórne); napisy w PDF pozostają tekstem wyszukiwalnym.
* Kolejność ciągów zewnętrznych: 1 otwory, 2 osie otworów i ściany wewnętrzne, 3 osie konstrukcyjne, 4 całość
  (odległości 10 / 7 mm) — ustala wywołujący (`dim_h/dim_v` z pozycjami).

## 5. Ograniczenia
* Symbole są „rozbite” na prymitywy (brak bloków/INSERT w DXF, brak atrybutów); kreskowania to geometria (brak
  obiektów HATCH z wzorem — wypełnienia pełne są HATCH SOLID).
* Wymiary to geometria + TEXT (brak obiektów DIMENSION/asocjatywności); indeks górny = osobny TEXT.
* Każda rzutnia ma własną kopię treści w przestrzeni modelu (adnotacje zależne od skali) — rzutnie tego samego
  fragmentu nie współdzielą geometrii.
* Brak usuwania linii niewidocznych i automatycznego generowania rzutów/przekrojów/elewacji z modelu 3D (IR) —
  silnik rysuje to, co dostanie (geometria 2D); generatory widoków z `model/budynek.yaml` to kolejny etap.
* Rozsuwanie kolizji obejmuje liczby wymiarowe w obrębie łańcucha; kolizje między różnymi obiektami (napisy
  pomieszczeń vs wymiary, symbole) rozwiązuje układ wywołującego lub maski (`mask=`).
* Łuki w PDF aproksymowane odcinkami (3°); w DXF zapisywane jako ARC/CIRCLE.
* Wzory linii nie są „dociągane” do przecięć na kreskach (poza osiami — dopasowanie długości wzoru do odcinka).
* Czcionka Liberation Sans (brak m.in. znaków ⁰ ≙ ∅ — używać Ø); w DXF styl wskazuje arial.ttf.
* Składanie arkuszy: znaki składania wg uogólnionej reguły DIN 824 A/PN-N-01603 (norma wycofana — przyjęcie).
* Symbole instalacji wewnętrznych wod.-kan./c.o./went. — brak aktualnej PN (R4-O01): oznaczenia praktyki,
  zawsze z legendą; numery IEC 60617 wg dawnej EN 60617-11 (wycofana).
