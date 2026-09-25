"""Mostki cieplne 2D wg PN-EN ISO 10211:2017 — „Dom LAMELA”.

Moduły:
* `geometria` — materiały (λ, pustki powietrzne wg ISO 6946 zał. D, rama/szyba z U_f/U_g), obszary (shapely), strefy
  brzegowe (θ, R_s), elementy flankujące, `Wezel`; budowa typowych węzłów z przegród modelu (`wezel_*`);
* `siatka` — siatka prostokątna MOS zagęszczana przy granicach materiałów, podwajanie podziałów, klasyfikacja komórek;
* `solver` — `ModelMOS` (warunki Robina h = 1/R_s, scipy.sparse SuperLU), `Rozwiazanie` (pole θ, strumienie,
  temperatury powierzchni, bilans, interpolacja w punkcie);
* `wyniki` — `oblicz_wezel` (kontrola siatki: Φ i ψ, bilans; L_2D, ψ_oi/ψ_e/ψ_i, f_Rsi przy R_si = 0,25), wykresy,
  raport Markdown, H_TB (ψ_oi — system wymiarów projektu), `eksport_wynikow` (JSON dla `fizyka.mostki`);
* `walidacja` — ISO 10211 zał. C przypadki 1 i 2 + przypadki analityczne; raport walidacji;
* `katalog` — katalog węzłów z modelu budynku (także nadproża, podokienniki, progi) i długości do H_TB (system oi),
  katalog demonstracyjny z wariantami, węzły z sekcji `wezly` modelu;
* `karta` — ciągłość izolacji („test ołówka”), kontrola wody i wilgoci, ocena, karta PNG i raport kart
  (`tools/katalog_mostkow.py`).

CLI: `PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d {walidacja|katalog} --out KATALOG [...]`.
"""
from .geometria import (LACZNIK_PRZYKLAD, MATERIALY_DOMYSLNE, PSI_DOMYSLNE_14683, ElementFlankujacy, Material,
                        Obszar, Strefa, U_podlogi_13370, U_w_okna, U_warstw, Warstwa, Wezel, lambda_eq_pustki,
                        material_pustki, material_rama, material_szyba, material_z_modelu, warstwy_z_modelu,
                        wezel_attyka, wezel_cokol, wezel_garaz, wezel_nadproze, wezel_naroznik_zewnetrzny,
                        wezel_oscieze_okna, wezel_podokiennik, wezel_prog_strop, wezel_rura_spustowa, wezel_sciana_1d,
                        wezel_wspornik)
from .siatka import Siatka, siatka_dla_wezla
from .solver import ModelMOS, Rozwiazanie
from .wyniki import WynikWezla, eksport_wynikow, oblicz_wezel, raport_katalogu, raport_wezla, zestawienie_HTB

__all__ = [n for n in dir() if not n.startswith("_")]
