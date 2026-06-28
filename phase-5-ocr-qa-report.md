# Phase 5 OCR QA Report

Date: 2026-06-28

## Scope

Added a low-cost OCR/visual-text QA planning lane for the `game-localization` skill.

This phase does not run OCR, does not call paid providers, and does not modify any game folder.

## Product Decision

OCR should be a capped QA helper, not the default translation path.

For personal-use localization, the cheapest useful order is:

1. Finish the text sample patch.
2. Capture a small set of representative gameplay/menu screenshots.
3. Run a local/manual OCR plan.
4. Use local OCR first.
5. Use cloud OCR or vision models only for a small failure set.

This avoids the expensive trap of scanning every image asset when most game images are icons, backgrounds, material textures, portraits, particles, or unused UI.

## Files Added Or Updated

- Added `scripts/plan_ocr_qa.py`
- Added `references/ocr-qa-strategy.md`
- Updated `SKILL.md`
- Updated `references/personal-use-mode.md`
- Updated `references/cost-control.md`
- Updated `references/translation-quality.md`
- Updated `references/engine-field-notes.md`

## What The New Script Does

`plan_ocr_qa.py` reads a Phase 1 `localization-audit.json` and optionally a screenshot folder.

It writes:

- `ocr-qa-plan.md`
- `ocr-qa-plan.json`
- `ocr-candidates.csv`

It:

- Ranks likely text-bearing images using path, extension, and size hints.
- Treats runtime screenshots as higher value than raw assets.
- Recommends manual screenshot review, RapidOCR, PaddleOCR, EasyOCR, Tesseract, cloud OCR, or vision-model fallback depending on evidence.
- Estimates local OCR/manual review time.
- Estimates paid OCR/vision cost only when explicit price inputs are supplied.
- Blocks paid OCR/vision steps unless budget and approval gates are satisfied.

It does not:

- Run OCR.
- Install OCR tools.
- Call remote APIs.
- Modify the source game folder.

## Tool Research

Useful mature routes:

- RapidOCR: free, open-source, offline-friendly OCR with default Chinese/English support and ONNX-style deployment options. Good default for this skill's low-cost local OCR sample.
- PaddleOCR: strong OCR toolkit with Chinese/English and multilingual model families. Better fallback when accuracy matters, but heavier to set up.
- EasyOCR: simple Python API and broad language support. Useful fallback, but PyTorch setup can be heavier.
- Tesseract: mature command-line OCR with many languages and output formats. Good for clean UI text, weaker for stylized game text.
- Google Cloud Vision / Azure Vision: useful for small paid OCR samples, priced by image/transaction tiers rather than text tokens.
- Vision language models: useful for hard screenshots such as "is there remaining English here?", but should not be used for high-volume OCR by default.

Sources checked:

- https://github.com/RapidAI/RapidOCR
- https://github.com/PaddlePaddle/PaddleOCR
- https://paddlepaddle.github.io/PaddleOCR/
- https://github.com/JaidedAI/EasyOCR
- https://github.com/tesseract-ocr/tesseract
- https://tesseract-ocr.github.io/
- https://cloud.google.com/vision/pricing
- https://azure.microsoft.com/en-us/pricing/details/computer-vision/

## Verification

Commands run:

```powershell
python -m py_compile generated-skill\game-localization\scripts\plan_ocr_qa.py
python generated-skill\game-localization\scripts\plan_ocr_qa.py "generated-skill\audit-output\real-games\Order of the Sinking Star Demo\localization-audit.json" --out "generated-skill\ocr-plan-output\real-games\Order of the Sinking Star Demo" --sample-size 30
python generated-skill\game-localization\scripts\plan_ocr_qa.py "generated-skill\audit-output\real-games\Tactical Breach Wizards\localization-audit.json" --out "generated-skill\ocr-plan-output\real-games\Tactical Breach Wizards" --sample-size 30
```

Results:

- `Order of the Sinking Star Demo`
  - Audited image assets: 1,232
  - Screenshots supplied: 0
  - Recommendation: `MANUAL_SCREENSHOTS_FIRST`
  - Gate: `READY_FOR_MANUAL_SCREENSHOT_REVIEW`
  - Meaning: do not OCR 1,232 assets first; capture representative runtime screenshots and only then decide whether OCR is worth it.

- `Tactical Breach Wizards`
  - Audited image assets: 0 in current shallow audit output
  - Screenshots supplied: 0
  - Recommendation: `SKIP_OCR_FOR_NOW`
  - Gate: `READY_WITHOUT_OCR`
  - Meaning: OCR is not currently the useful next step; continue the text lane/runtime manual review.

## Remaining Risks

- No real OCR engine was installed or executed in this phase.
- Screenshot capture automation is not implemented.
- OCR hit parsing and confidence normalization are not implemented.
- Image editing/art-text replacement is still out of scope.
- Packed texture extraction/conversion, especially `.dds` or atlases, still needs tool-specific handling.

## Next Recommended Goal

Add a small optional local OCR adapter only after choosing the first supported tool, preferably RapidOCR or PaddleOCR.

The adapter should:

- Read `ocr-candidates.csv` or a screenshot folder.
- Write an OCR hit list.
- Never call paid tools by default.
- Feed only unresolved/hard screenshots into a paid cloud or vision route after budget approval.
