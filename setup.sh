#!/bin/bash
# Deja listo ./assets (tipografías + logo) al lado de lr_carrusel2.py. Correr una vez por sesión.
set -e
cd "$(dirname "$0")"; mkdir -p assets/fonts; cp -n lr_logo.png assets/lr_logo.png 2>/dev/null || true
B=https://raw.githubusercontent.com/google/fonts/main/ofl
for f in anton/Anton-Regular.ttf bebasneue/BebasNeue-Regular.ttf barlowcondensed/BarlowCondensed-ExtraBold.ttf barlowcondensed/BarlowCondensed-Medium.ttf \
  "archivo/Archivo%5Bwdth,wght%5D.ttf" "montserrat/Montserrat%5Bwght%5D.ttf" "roboto/Roboto%5Bwdth,wght%5D.ttf" \
  "playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf" "playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf" "jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf" \
  "fredoka/Fredoka%5Bwdth,wght%5D.ttf"; do
  o="assets/fonts/$(basename "$f" | sed 's/%5B.*//;s/\.ttf//').ttf"; [ -s "$o" ] || curl -sSfL -o "$o" "$B/$f"; done
ls assets/fonts | wc -l; ls -la assets/lr_logo.png
