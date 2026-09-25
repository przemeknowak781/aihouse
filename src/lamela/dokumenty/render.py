"""HTML → PDF (Chromium headless przez Playwright) i narzędzia PDF (PyMuPDF).

Chromium obsługuje stronicowanie CSS (``@page`` z polami marginesowymi ``@top-left`` … ``@bottom-right``,
``counter(page)`` / ``counter(pages)``, strony nazwane ``page: …``), powtarza ``<thead>`` tabel na kolejnych
stronach i zachowuje odnośniki wewnętrzne ``<a href="#id">`` jako adnotacje z docelową stroną — z nich system
odczytuje numery stron do spisu treści (render dwuprzebiegowy, ``dokument.py``).

Ścieżka przeglądarki: zmienna środowiskowa ``LAMELA_CHROMIUM`` albo ``/opt/pw-browsers/chromium``.
Czcionki: wyłącznie lokalne (Liberation Sans / DejaVu Sans przez fontconfig) — bez dostępu do internetu.
"""
from __future__ import annotations

import atexit
import os
import threading

import pymupdf

CHROMIUM = os.environ.get("LAMELA_CHROMIUM", "/opt/pw-browsers/chromium")


class _Przegladarka:
    """Jedna instancja Chromium na proces (uruchamiana przy pierwszym renderze, zamykana przy wyjściu)."""
    _lock = threading.Lock()

    def __init__(self):
        self._pw = None
        self._browser = None

    def _start(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(executable_path=CHROMIUM, headless=True,
                                                 args=["--font-render-hinting=none", "--disable-gpu"])
        atexit.register(self.zamknij)

    def zamknij(self):
        try:
            if self._browser is not None:
                self._browser.close()
            if self._pw is not None:
                self._pw.stop()
        except Exception:
            pass
        self._browser = self._pw = None

    def pdf(self, html: str) -> bytes:
        with self._lock:
            if self._browser is None:
                self._start()
            page = self._browser.new_page()
            try:
                page.set_content(html, wait_until="load")
                page.evaluate("document.fonts.ready.then(() => true)")
                return page.pdf(prefer_css_page_size=True, print_background=True, tagged=True, outline=False)
            finally:
                page.close()


_PRZEGLADARKA = _Przegladarka()


def html_na_pdf(html: str) -> bytes:
    """Renderuje kompletny dokument HTML (style i obrazy osadzone) do PDF. Rozmiar strony z CSS ``@page``."""
    return _PRZEGLADARKA.pdf(html)


def zamknij_przegladarke():
    _PRZEGLADARKA.zamknij()


# ------------------------------------------------------------------------------------------------- narzędzia PDF
def kotwice(doc: pymupdf.Document) -> dict[str, int]:
    """Mapa ``id kotwicy → indeks strony (od 0)`` z odnośników nazwanych utworzonych przez Chromium."""
    wynik: dict[str, int] = {}
    for i, page in enumerate(doc):
        for ln in page.get_links():
            nd = ln.get("nameddest") or ln.get("name")
            if ln.get("kind") in (pymupdf.LINK_NAMED, pymupdf.LINK_GOTO) and nd and ln.get("page", -1) >= 0:
                wynik.setdefault(nd, ln["page"])
    return wynik


def linki_na_goto(doc: pymupdf.Document, uri_mapa=None):
    """Zamienia odnośniki nazwane (LINK_NAMED) na jawne GoTo (zachowują się przy scalaniu plików) oraz —
    opcjonalnie — odnośniki URI rozpoznane przez ``uri_mapa(uri) -> indeks strony | None`` na GoTo."""
    for page in doc:
        nowe, stare = [], []
        for ln in page.get_links():
            cel = None
            if ln.get("kind") == pymupdf.LINK_NAMED and ln.get("page", -1) >= 0:
                cel = ln["page"]
            elif ln.get("kind") == pymupdf.LINK_URI and uri_mapa is not None:
                cel = uri_mapa(ln.get("uri", ""))
            if cel is not None and 0 <= cel < doc.page_count:
                stare.append(ln)
                nowe.append({"kind": pymupdf.LINK_GOTO, "from": ln["from"], "page": int(cel),
                             "to": pymupdf.Point(0, 0), "zoom": 0})
        for ln in stare:
            page.delete_link(ln)
        for ln in nowe:
            page.insert_link(ln)


def rozmiar_mb(sciezka) -> float:
    """Rozmiar pliku w MB (10⁶ B — jednostka dziesiętna SI, jak w RPB § 2b ust. 3 „150 MB”)."""
    return os.path.getsize(sciezka) / 1_000_000
