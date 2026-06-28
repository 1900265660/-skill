# OCR QA Strategy

Use OCR as a late, capped QA lane. Do not OCR every game asset by default.

## Principle

Screenshots first, candidate assets second, full asset OCR almost never first.

Image/OCR work becomes expensive because most game images are not translatable text:

- Icons, portraits, backgrounds, particles, masks, and material textures often produce noise.
- Text-bearing images may be packed in atlases or engine archives.
- Artistic logos and stylized fonts usually need manual art edits, not just OCR.
- Runtime screenshots show player-visible text; raw assets may include unused or hidden textures.

## Default Personal-Use Path

1. Finish text lane sample patch and static QA first.
2. Capture 10-30 representative screenshots manually from menus, dialogue, inventory, settings, tutorial, battle UI, and credits.
3. Run the OCR QA planner:

   ```bash
   python scripts/plan_ocr_qa.py "path/to/localization-audit.json" --out "path/to/ocr-plan" --screenshots-dir "path/to/screenshots" --sample-size 30
   ```

4. Use local OCR on the selected sample only.
5. Review OCR hits manually. Treat them as "possible untranslated visible text", not final truth.
6. Expand only when screenshots prove image text is a real blocker.

## Tool Order

Prefer tools in this order for low-cost personal use:

1. **Manual screenshot review**
   - Best first step when the user has no OCR setup.
   - Zero API cost.
   - Good enough to decide whether image text is common.

2. **RapidOCR**
   - Good default local option for Chinese/English OCR.
   - Free and offline after setup.
   - Uses ONNX-style deployment options and is easier to fit into a lightweight workflow than a large vision model.
   - Source: https://github.com/RapidAI/RapidOCR

3. **PaddleOCR**
   - Stronger full OCR toolkit and model family.
   - Good when RapidOCR misses too much or when detection/recognition model choice matters.
   - Heavier dependency/setup than RapidOCR.
   - Source: https://github.com/PaddlePaddle/PaddleOCR and https://paddlepaddle.github.io/PaddleOCR/

4. **EasyOCR**
   - Simple Python API, supports many languages and scene-text workflows.
   - Useful fallback when Paddle/Rapid setup is inconvenient.
   - Can be heavier because it depends on PyTorch.
   - Source: https://github.com/JaidedAI/EasyOCR

5. **Tesseract**
   - Mature command-line OCR with many languages and output formats.
   - Good for clean UI screenshots and simple printed text.
   - Often weaker on stylized, outlined, rotated, or low-resolution game text.
   - Source: https://github.com/tesseract-ocr/tesseract and https://tesseract-ocr.github.io/

6. **Cloud OCR**
   - Use only for small samples or arbitration when local OCR fails.
   - Current official pricing must be checked before paid use.
   - Google Cloud Vision and Azure Vision price OCR by image/transaction tiers, not by text tokens.
   - Sources: https://cloud.google.com/vision/pricing and https://azure.microsoft.com/en-us/pricing/details/computer-vision/

7. **Vision language models**
   - Useful for "does this screenshot still contain English?" or interpreting stylized UI.
   - Usually overkill for high-volume OCR.
   - Must pass the same pricing/budget approval gate as translation providers.

## Cost Control

Avoid these defaults:

- Full OCR over all image assets.
- Sending every screenshot to a paid vision model.
- Treating OCR output as trusted translation memory.
- Starting image editing before proving the text lane works.

Use these controls:

- Cap first pass at 10-30 screenshots or candidate images.
- Prefer local OCR with zero API spend.
- Prefer screenshot OCR over asset OCR.
- Use path/size hints to rank candidate assets before OCR.
- Record which screenshots produced untranslated text.
- Only send the small failure set to a cloud OCR or vision model if local tools fail.

## Go / No-Go Labels

- `SKIP_OCR_FOR_NOW`: no clear image-text evidence; continue text lane.
- `SCREENSHOT_OCR_SAMPLE`: screenshots exist; run local OCR/manual review on screenshots first.
- `MANUAL_SCREENSHOTS_FIRST`: many assets, weak text hints; capture screenshots before asset OCR.
- `LOCAL_PREFILTER_THEN_SAMPLE`: image volume is high; OCR only ranked candidates.
- `LOCAL_OCR_SAMPLE`: small enough for local sample OCR.
- `CAUTION_IMAGE_HEAVY`: image text appears central to the game; warn user before continuing.

## When To Stop

Stop and ask the user before expanding image work when:

- More than a small sample requires art editing.
- Text is baked into logos, signs, comics, maps, or stylized title cards.
- Fonts or atlases cannot be replaced safely.
- Screenshots show important untranslated text but no editable text source exists.
- Paid OCR/vision cost exceeds the user-approved budget.

## Output Expectations

An OCR QA pass should produce evidence, not silent changes:

- `ocr-qa-plan.md`
- `ocr-candidates.csv`
- OCR hit list with screenshot/image path, recognized text, confidence if available, and human decision.
- Follow-up action: ignore, translate text lane, edit image manually, defer, or stop.

Do not mark a release complete while OCR/image-text evidence is unreviewed.
