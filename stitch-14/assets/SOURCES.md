# Branding asset provenance

- Source: user-provided `stitch_ (14).zip` (Google Drive ID `10Fv1FbF9_gcCwGp8wAWU_kIR4glG7_Oi`).
- ZIP SHA-256: `040c2c6c74384f27ef253a92e4b6f8a2402118564ba38f4f3b9a24f1cb088e9f`.
- `rotbeland-logo.png`: faithful 54×54 pixel crop of `stitch_/_1/screen.png` (1600×1432 pixels), crop rectangle `[1219, 45, 1273, 99]`. No redraw, AI generation or logo substitution. The original HTML links an external logo; no independent logo image is bundled in the source ZIP. Screenshot resolution limits print sharpness.
- `telegram.svg`, `instagram.svg`: original paths from the first planner HTML footer, with local SVG namespace, 96×96 dimensions, and source gold `#775a00` fill. PNG counterparts rasterized with PyMuPDF for Word compatibility.
- The completed HTML retains each source footer's original inline SVG icons; Word uses the local PNGs. Only these three small brand images are embedded in Word; all form text and tables remain editable.
- Vazirmatn web font/license and DejaVu symbol subset/license are retained from the finalized Stitch13 pipeline. Word's full Vazirmatn regular/bold fonts are embedded from the repository's root `assets/word-fonts/`.

To reproduce the logo crop with PyMuPDF, open the source PNG as a document, crop `Rect(1219,45,1273,99)*0.75`, and render with `Matrix(4/3,4/3)` (the source image is 96 DPI).
