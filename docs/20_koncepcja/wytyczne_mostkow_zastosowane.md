# Zmiany wprowadzone przez kopię agenta syntezy (do weryfikacji przez oryginał i audytorów)

Stan: 2026-09-25, ok. 04:05 UTC. Kopia agenta syntezy (subagent a3a8ae3b05a6e1fbd) zakończyła edycje na polecenie koordynatora.
Kopia **nie otrzymała** wiadomości z wytycznymi mostków. Blok „montaż stolarki, osłony, progi — wytyczne z symulacji mostków 2D”
w `tools/buduj_model.py` wstawił drugi agent. Kopia go nie zmieniała. Poniżej jest pełna lista zmian kopii, z uzasadnieniem.

## 1. `tools/buduj_model.py` (plik modelu parametrycznego)

| Sekcja / element | Zmiana | Powód |
|---|---|---|
| 5. Otwory — przeszklenie E (`E_KW`) | Kwatery 1,90 / 1,90 / 2,34 / 2,34 / 2,92 m (x 0,30–2,20–4,10–6,44–8,78–11,70). Wcześniej 2,335 m | QA arkuszy: łańcuch wymiarowy na rzucie P1 sumował się do 1259,9 cm zamiast 1260 cm. Moduł 0,01 m. Słupy SL3/SL4 nadal leżą w jednej linii ze słupkami boksu C (przeszczep J2) |
| 5. Otwory — boks C `O1-01` | x 4,10–11,12 (3 × 2,34 m). Nadproże B2 przedłużono do x 11,37. Bok ramy C (SL8) przesunięto na x 11,195 | Zgodność z podziałem przeszklenia E |
| 5. Otwory `O0-06`, `O0-10`, `O0-21`, `O0-14`, `O0-16`, `O1-10`, `O2-10` | Przesunięto je (drzwi gospodarcze x 12,35–13,25; doświetle 11,25–11,60; drzwi kuchnia–przedsionek y 0,35–1,25; drzwi łazienek pionu SI x 4,20–5,10). Blat kuchni zaczyna się od y 1,40 | Walidator zgłaszał ostrzeżenia „otwór koliduje z połączeniem ściany”. Po zmianie jest 0 ostrzeżeń |
| 7. Wsporniki — nowy `IZ-ST2Z` | Warstwa wełny 20 cm z podsufitką pod stropem ST2Z (P2 nad powietrzem zewnętrznym, wspornik bryły A) | Ciągłość izolacji (brief §9.1). Na przekroju B-B nie było ocieplenia spodu wspornika, bo sufit `SUF-ZEW` nie jest rysowany poza obrysem P1 |
| 7. Wsporniki — nowe `SW1`, `WYL1` | Szkło świetlika nad klatką (otwór w D1 x 6,10–8,30, y 7,55–8,55) i pokrywa wyłazu dachowego 0,90 × 0,90 m | Otwory w dachu D1 nie miały przekrycia. Góra elementów ≤ +9,75, czyli poniżej attyki +9,776 |
| 12. Wyposażenie | `zlewik` zamieniono na `zlew` (opis „zlewik gospodarczy”). Płytę indukcyjną przeniesiono na środek wyspy | Generator widoków nie zna typu `zlewik` |
| 11. Działka | T3 i U6 przesunięte razem z drzwiami O0-06. Branża rur deszczowych: `kan_deszcz` | Spójność geometrii |
| 10. Zapis — `fl()` | Usunięto znacznik końca dokumentu „...” z wartości skalarnych | Plik budynek.yaml miał błąd składni YAML |

## 2. Rdzeń i generatory (poprawki zgodności z SCHEMAT_MODELU.md p. 6)

* `src/lamela/model.py`, walidacja `dachy[].wpusty`: walidator przyjmuje teraz także format ze schematu p. 6 (`{xy: [x, y], dn, podgrzewany}`). Punkty `[x, y]` działają jak dotąd.
* `src/lamela/views/plan.py`, rzut dachu: wpusty w formacie słownikowym są odczytywane z `xy`. Przedtem arkusz PB-AR-04 kończył się błędem `float() … dict`.

## 3. Konfiguracja i wyniki wygenerowane

* `model/arkusze.yaml`: przekroje jawne (W-315):
  * A-A: `{id: A, x: 6.55, patrz: E}` — przez schody, boks C i bryłę A;
  * B-B: `{id: B, y: 3.30, patrz: N}` — przez wspornik A, strefę dzienną i garaż.
* Kopia ponownie wygenerowała `model/budynek.yaml`, `model/dzialka.yaml`, `model/wyposazenie.yaml` i `model/instalacje.yaml`. Walidacja: 0 błędów, 0 ostrzeżeń.
* Kopia wygenerowała arkusze `projekt/01_koncepcja/widoki/` (10 arkuszy, QA OK) oraz model 3D w `projekt/07_model_3D/wstepne/` (`budynek.glb`, bez renderów).

## 4. `tools/podglad_modelu.py`

Kopia raz omyłkowo nadpisała ten plik. Następnie go odtworzyła: pierwsze 154 linie pochodzą z commitu 886f846 (nagłówek i `rzut()` oryginału), a za nimi są wszystkie fragmenty dopisane później przez oryginał. Plik jest poprawny składniowo. Należy on do oryginału i kopia go już nie zmienia.

## 5. Do sprawdzenia przez oryginał

1. Czy zachować `IZ-ST2Z`, `SW1` i `WYL1` jako elementy `wsporniki_plyty`? Alternatywa: rozszerzyć generator IR o rysowanie `stropy[].sufit` poza obrysem kondygnacji niżej.
2. Czy zachować zmianę kwater E i boksu C na 2,34 m?
3. Czy przyjąć poprawki zgodności w `model.py` i `plan.py`? Zespół rdzenia powinien je potwierdzić.
