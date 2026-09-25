"""Rzuty i schematy instalacji (PT-IS, PT-IE) na podkładzie architektonicznym — typy widoków rejestrowane w
``lamela.views.sheets`` (moduł ładowany automatycznie przy nieznanym typie widoku).

Typy widoków (plik konfiguracji arkuszy, np. ``model/arkusze_is.yaml`` / ``model/arkusze_ie.yaml``):

* ``inst_rzut`` — rzut instalacji na podkładzie AR; parametry: ``branza`` (kod poniżej), ``kond`` (``P0``…/``dach``),
  opcjonalnie ``tytul_widoku``; ``opcje``: ``meble`` (bool, podkład z meblami), ``opisy_pomieszczen`` (bool).
    - ``IS-W``  woda zimna / ciepła / cyrkulacja, zestaw wodomierzowy, rozdzielacze, zasobnik, piony, zawory,
    - ``IS-K``  kanalizacja sanitarna: podejścia, piony, rewizje, wentylacja pionów, spadki, średnice, przykanalik,
    - ``IS-D``  odwodnienie dachów: wpusty, przelewy awaryjne, rury spustowe, spadki (``dachy[]`` modelu, § 6),
    - ``IS-CO`` ogrzewanie: PC (jednostka zewn. i moduł), bufor, zasobnik, rozdzielacze, pętle podłogówki (obszar,
      rozstaw, długość z obliczeń), piony c.o.,
    - ``IS-WM`` wentylacja mechaniczna z odzyskiem ciepła: centrala, kanały, anemostaty z wydatkami, czerpnia/wyrzutnia,
    - ``IE-O``  oświetlenie: oprawy, łączniki, obwody; ``IE-G`` gniazda i zasilania urządzeń; ``IE-T`` teletechnika
      (światłowód, LAN, TV, domofon, SSWiN); ``IE-PV`` fotowoltaika (moduły, falownik, trasy DC, SPD);
      ``IE-U`` uziom, połączenia wyrównawcze, ochrona odgromowa (wg analizy ryzyka z obliczeń).
* ``inst_schemat`` — schematy (bez skali): ``schemat``: ``kanalizacja`` (rozwinięcie pionów), ``woda`` (rozwinięcie
  instalacji wodociągowej), ``pc`` (schemat PC / c.w.u. — ``obliczenia.sanitarne.schemat_pc``), ``rg`` (schemat
  rozdzielnicy — ``obliczenia.elektryka.schemat_rg``); schematy matplotlib odtwarzane wektorowo w silniku.

Dane: model (``budynek.yaml``: dachy § 6, pomieszczenia, otwory), ``instalacje.yaml`` (lokalizacje, piony, przybory
dodatkowe), ``wyposazenie.yaml`` (przybory, urządzenia) i wyniki bibliotek ``lamela.obliczenia`` uruchamianych na
aktualnym modelu (``dane.oblicz``). Braki danych → ``wspolne.braki_danych`` (plik Markdown) i oznaczenie
[DO UZUPEŁNIENIA] na rysunku. Konfiguracja ``wspolne``: ``instalacje``, ``wyposazenie`` (ścieżki; domyślnie obok
budynku), ``braki_danych`` (ścieżka pliku braków).
"""
from __future__ import annotations

import importlib

from ...draft.core import Viewport
from ..sheets import register_view
from .wspolne import zapisz_braki

GEN = {
    "IS-W": ("is_woda", "RysW", "INSTALACJA WODOCIĄGOWA"),
    "IS-K": ("is_kan", "RysK", "KANALIZACJA SANITARNA"),
    "IS-D": ("is_desz", "RysD", "ODWODNIENIE DACHÓW"),
    "IS-CO": ("is_co", "RysCO", "OGRZEWANIE"),
    "IS-WM": ("is_went", "RysWM", "WENTYLACJA MECHANICZNA"),
    "IE-O": ("ie_rzut", "RysO", "INSTALACJA OŚWIETLENIA"),
    "IE-G": ("ie_rzut", "RysG", "INSTALACJA GNIAZD WTYCZKOWYCH I ZASILANIA URZĄDZEŃ"),
    "IE-T": ("ie_rzut", "RysT", "INSTALACJE TELETECHNICZNE"),
    "IE-PV": ("ie_pv", "RysPV", "INSTALACJA FOTOWOLTAICZNA"),
    "IE-U": ("ie_pv", "RysU", "UZIEMIENIA, POŁĄCZENIA WYRÓWNAWCZE, OCHRONA ODGROMOWA"),
}


def inst_rzut(ctx, spec: dict, scale: float, opts: dict):
    from . import dane
    br = str(spec.get("branza") or opts.get("branza") or "IS-W").upper()
    if br not in GEN:
        raise ValueError(f"nieznana branża instalacji '{br}' ({', '.join(GEN)})")
    mod, cls, nazwa = GEN[br]
    kid = str(spec.get("kond", "P0"))
    W = dane.oblicz(ctx)
    C = getattr(importlib.import_module(f"{__name__}.{mod}"), cls)
    vp = Viewport(scale, "x")
    rys = C(vp, ctx, W, kid, spec, opts)
    title = spec.get("tytul_widoku") or f"{nazwa} — {rys.storey_name()}"
    vp.title = vp.name = title
    res = rys.run()
    for u in W.korekty:
        ctx.note("instalacje (obliczenia)", u)
    zapisz_braki(ctx, rys.br)
    return vp, res, title


def inst_schemat(ctx, spec: dict, scale: float, opts: dict):
    from . import dane, schematy
    W = dane.oblicz(ctx)
    vp, res, title = schematy.rysuj(ctx, W, spec, scale, opts)
    zapisz_braki(ctx, "IE" if str(spec.get("schemat", "")).lower() == "rg" else "IS")
    return vp, res, title


register_view("inst_rzut", inst_rzut, rodzaj="rzut instalacji")
register_view("inst_schemat", inst_schemat, rodzaj="schemat instalacji")
