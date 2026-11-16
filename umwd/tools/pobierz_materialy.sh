#!/bin/bash
# Pobiera materiały organizatora konkursu z folderu Google Drive (udostępnionego przez link).
# Pliki z WYNIKAMI konkursu są celowo POMIJANE (decyzja Inwestora: nie bierzemy pod uwagę
# informacji o projektach zwycięskich/konkurencyjnych).
set -u
DST="${1:-/home/user/aihouse/umwd/00_materialy/_raw}"
mkdir -p "$DST"; cd "$DST"
get() { # id nazwa
  local id="$1" name="$2"
  [ -s "$name" ] && { echo "jest: $name"; return; }
  for i in 1 2 3 4; do
    curl -sS -L --retry 3 -o "$name.part" "https://drive.usercontent.google.com/download?id=${id}&export=download&confirm=t" && mv "$name.part" "$name" && { echo "OK: $name $(stat -c%s "$name")"; return; }
    sleep $((2**i))
  done
  echo "BŁĄD: $name"
}
get 1YyV90cRbF2I_HkrZJTs9V77DmE4Z-Oyh "1_Ogloszenie_o_konkursie_2025-OJS237-00815277-pl.pdf"
get 1NpEIYwg9Sqb42FqJHN3iNSn368lYfRiy "2_Regulamin_Konkursu-sig.pdf"
get 1Eo3dSSLK0kluIOQ20ywgP5wZqWCj0SnO "1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.pdf"
get 1dHxn6-Cq8rq4VsgXJPZh8eGq4FRrAY4b "1089_Sprostowanie_Regulaminu_Konkursu_nr_1-sig.pdf"
get 1a5WMzOQBdYHAL_NHRaCqKZHY104IPS52 "1089_Zmiana_tresci_Regulaminu_Konkursu_nr_1-sig.pdf"
get 1IlhayQnr2slUPzV3UjRPBHB_D4YMAcv7 "1089_Notatka_z_wizji_lokalnej.pdf"
get 12xU5DvKCg44SLBBoLg3zQoZ_MyBxw1ga "Inwentaryzacja_Slowackiego_5_lok.6-6A.pdf"
get 1BfNCXAee1_fFUQvPqHBCSSmpu6Cq4udn "Miejsce_skladania_opracowan_studialnych_i_prac_konkursowych.jpg"
get 10u0l3LrcvOohkVG0ThhPEG3yvcHrgKEM "F.06_Oswiadczenie_Doswiadczenie_Uczestnika_wer.2.pdf"
get 1AHGILezu1icBHFqRJ5pPWlx7CSvncAib "F.06_Oswiadczenie_Doswiadczenie_Uczestnika_wer.2.docx"
get 1gxWFKIuy1RiUkN2opLnsx9zbZ72n7u7z "4.Zalaczniki_Formalne_F.03-F.16_edytowalne.zip"
for n in 1:1AE8MGWuYgaMX34CPyBee8Aps9dWEi7IO 2:1W8af9AJEtEaFH98aXRrLDfYZfl6Kv93C 3:14QPbPVlsPixOVj2mDViOOLVP5r1bxSXe 4:1lYO280YB_qis_jCBFr-_WkvL9wAG4jMd 5:1AEzW6H3FnDvhu4eAHO2_djdcACqHjz_C 6:1fxV-CTXCq6G6j3GuRzUPLE85_7VOPTwQ 7:1m6jKIcyUaElxE3H0tFn6Mo_aL6cIieaU 8:1iEU6_ePpjP8f6iGf2OPYLZyJ9UZr-mnW 9:1TaPr1Mp94tPZVe_z9XJxBUV9RspOqSUP 10:1qRLlRA-IhZofuhPsT65zS92_zOI2QgFh 11:1TtKlWeVpLo4CjkiwoyYhrdfHeKKYyB91 12:1WcSySKzX1FgNfXuAirv-8Za4WpMV7vdh 13:1R98htogyy4gvQ7W45rc3-y3L6cv0O4Lw 14:1yGhxgI4mWKQq2D08AaPWVdrjVIHqWfnY 15:1wkclvuwd187dFJfgiDAEeKlYrECQTuZZ 16:1-P-s2SYbuuW_A_yjWF7T0c2EnIYEDgjc 17:1pQCmboq3wmAWXWpFwAQO9gxpP_cnQnQF 18:1vDOM7B-1AXGhK4L_MiBhc-r6zUSScVXU 19:1KLCHpHFoFpD5qY8uluGY8lCirnPp9qgk 20:13jOrWrTRo7t14r8MWeuWA9TTDPisefpI 21:1InEFH0HIVP63q9waG0mgmqUhsM7PUsxC; do
  get "${n#*:}" "$(printf '1089_Wyjasnienia_tresci_Regulaminu_nr_%02d-sig.pdf' "${n%%:*}")"
done
get 1saAnthST5yqe4PrArJZG01I7s_a8AGai "3.Zalaczniki_Formalne_F.01-F.17_PDF.zip"
get 1cWQXsT2QWACtIY3NVF7N7uWvJw_2WYlf "5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026.zip"
get 1aQVNG5orCtjSURzpGdPTI9TAwSw46uAs "5_Zalaczniki_Merytoryczne_M.01-M.14_oryginal.zip"
# POMINIĘTE CELOWO (wyniki / informacje o konkurencji):
#  - Informacja o wynikach rozstrzygnięcia Konkursu na stronę-sig.pdf
#  - Informacja o wynikach rozstrzygnięcia Etapu_I-sig.pdf
#  - Informacja o wynikach dopuszczenia do udzialu w konkursie-sig.pdf
echo KONIEC
