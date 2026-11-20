#!/usr/bin/env bash
# Eksport arkuszy DXF (lamela.views) do DWG AutoCAD 2018 (AC1032) darmowym ODA File Converter (Open Design Alliance).
# Użycie: projekty/dobrzykowice/narzedzia/eksport_dwg.sh <katalog_ODAFileConverter> [wersja, domyślnie ACAD2018]
#   katalog_ODAFileConverter — katalog z binarką ODAFileConverter (np. rozpakowany pakiet .deb ze strony
#   https://www.opendesign.com/guestfiles/oda_file_converter: usr/bin/ODAFileConverter_<wersja>).
# Bez ekranu uruchamiany przez xvfb-run (wtyczka Qt xcb); wymaga bibliotek libopengl0, libegl1, libxkbcommon-x11-0.
set -euo pipefail
ODA="${1:?podaj katalog ODAFileConverter}"
VER="${2:-ACAD2018}"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
IN="$(mktemp -d)"; OUT="$(mktemp -d)"
trap 'rm -rf "$IN" "$OUT"' EXIT
cp "$HERE"/rysunki/*.dxf "$IN"/
xvfb-run -a env LD_LIBRARY_PATH="$ODA:$ODA/lib" QT_PLUGIN_PATH="$ODA/plugins" QT_QPA_PLATFORM=xcb \
    "$ODA/ODAFileConverter" "$IN" "$OUT" "$VER" DWG 0 1 "*.dxf"
if ls "$OUT"/*.err >/dev/null 2>&1; then echo "Błędy audytu:"; cat "$OUT"/*.err; exit 1; fi
cp "$OUT"/*.dwg "$HERE"/rysunki/
ls -la "$HERE"/rysunki/*.dwg
