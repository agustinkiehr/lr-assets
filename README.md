# lr-assets — La Redacción

Motor y recursos de la skill `la-redaccion-carrusel-v2` (carruseles 4:5, segunda generación).

- `lr_carrusel2.py` — motor: un spec.json → placas PNG 1080×1350 + ZIP + `_preview.png`.
- `lr_logo.png` — logo LR oscuro original (512 px, fondo transparente). No redibujar ni recolorear.
- `setup.sh` — baja las tipografías de Google Fonts y arma `assets/`.
- `examples/*.json` — un spec de ejemplo por formato (las rutas `fotos/...` son de muestra).

Uso: `bash setup.sh && python3 lr_carrusel2.py examples/historias.json`
