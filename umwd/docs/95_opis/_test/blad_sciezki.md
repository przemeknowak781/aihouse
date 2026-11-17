<!-- FIXTURE NEGATYWNY: każdy wiersz z placeholderem bez słowa „OK” zawiera błąd i musi zostać zgłoszony z numerem wiersza. -->
# Test błędnych ścieżek

Poprawny placeholder (OK): {{K:bilans.PU_m2|2}} m².

Brak klucza: {{K:bilans.PU_nieistniejace|2}} m².

Brak elementu listy: {{K:bryly[id=X].pow_rzutu_m2|1}} m².

Indeks poza listą: {{K:teren.wieza_2m.7|2}}.

Tekst z formatem liczbowym: {{K:meta.wersja|2}}.

Nieznane źródło: {{X:bilans.PU_m2|2}}.

Nieznany format: {{K:bilans.PU_m2|dwa}}.

Lista bez selektora: {{B:kondygnacje.pomieszczenia|0}}.

Niedomknięty placeholder: {{K:bilans.PU_m2|2 m².
