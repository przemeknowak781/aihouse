# Dopasowanie kamery do zdjęć F.17.A i F.17.B — metadane wyjściowe

Źródło: metadane EXIF/XMP (DJI) plików organizatora `F.17.A_widok z lotu ptaka od strony wschodniej_wer.01.jpg`
i `F.17.B_widok z lotu ptaka od strony zachodniej_wer.01.jpg` (Załącznik F.17 do Regulaminu), odczyt: PIL (python3 -I).
Przeliczenie WGS-84 → PL-2000 strefa 6 (EPSG:2177): pyproj. Układ lokalny projektu: e = Y2000 − 6 433 500,00; n = X2000 − 5 664 100,00.
Położenie Słońca: algorytm NOAA (`umwd/src/umwd/sun.py`), czas z EXIF (OffsetTime +01:00 = CET).

| parametr | F.17.A (od wschodu) | F.17.B (od zachodu) |
|---|---|---|
| dron / kamera | DJI Air 3, FC8282, obiektyw 24 mm ekw. (f = 6,72 mm), f/1,7 | jw. |
| data i godzina zdjęcia | 29.10.2025, 11:38:00 CET | 29.10.2025, 11:57:36 CET |
| GPS (WGS-84) | 51,108316679 N; 17,055469768 E | 51,107810447 N; 17,049754529 E |
| PL-2000/6: Y (E), X (N) | 6 433 856,39; 5 664 124,10 | 6 433 455,45; 5 664 072,94 |
| układ lokalny e, n [m] | 356,4; 24,1 | −44,6; −27,1 |
| wysokość względna (od startu) | 87,8 m | 50,7 m |
| wysokość „absolutna” DJI | 219,7 m (GpsFusionAlt — niepewna, do kalibracji) | 182,6 m |
| gimbal: yaw / pitch / roll | −89,2° (kierunek ≈ zachód) / −12,9° / 0,0° | +39,2° (≈ płn.-wsch.) / −11,4° / 0,0° |
| rozdzielczość pliku organizatora | 8470 × 4475 px (oryginał sensora 8000 × 5632 → plik po obróbce w Photoshopie: skalowanie i/lub kadrowanie pionowe, możliwa korekcja dystorsji) | 7962 × 4505 px |
| Słońce w chwili zdjęcia | azymut 180,7°, wysokość 25,3° | azymut 185,9°, wysokość 25,1° |

Wnioski (wniosek własny):
1. Wymiary pliku ≠ wymiary sensora, więc ogniskowa w pikselach i punkt główny muszą zostać **wyznaczone** (rozwiązanie PnP na
   ≥ 8 punktach kontrolnych o znanych współrzędnych 3D: narożniki budynków z mapy do celów projektowych + wysokości,
   pylony Mostu Grunwaldzkiego, krawędzie nabrzeża), a EXIF służy jako przybliżenie startowe (pozycja, yaw, pitch, 24 mm).
2. Wizualizacje 1 i 2 wklejane w zdjęcia muszą mieć Słońce z azymutu ≈ 181–186° na wysokości ≈ 25° (cienie na północ),
   jesienną kolorystykę zieleni i ekspozycję/balans bieli dopasowane do zdjęcia (WB ≈ 5500 K wg XMP).

**Wynik kalibracji (2026-11-16):** kamery wyznaczone z punktów kontrolnych – `photomatch_F17.md`, `model/kamery_F17.json`
(generator `tools/photomatch_F17.py`). Potwierdzono, że F.17 to kadr panoramy 8000×5632 (×1,25), a nie pojedyncza klatka 24 mm;
ogniskowa F.17.A = 4058 px (Blender 17,25 mm przy sensorze 36 mm), F.17.B = 3876 px (17,52 mm), wysokość kamer 203,9 / 166,2 m n.p.m.
