# Translation Tool Handoff

Date: 2026-06-28

## Status

Translation tool implementation has resumed for the fixture-harness slice.

This file remains the handoff for future provider adapters, OCR adapters, runtime screenshot automation, Godot package strategy, and other implementation work.

## Current Implemented Skill Capabilities

- Phase 1: read-only packaged game audit with `scripts/scan_project.py`.
- Phase 2: text inventory extraction with `scripts/extract_inventory.py`.
- Phase 2.5: inventory validation with `scripts/validate_inventory.py`.
- Phase 3: cost/time estimate and provider dry-run gating with `scripts/estimate_cost.py`.
- Phase 4: patch generation and static QA with `scripts/generate_patch.py`.
- Phase 4.5: personal-use sample translation package with `scripts/prepare_sample_translation.py`.
- Phase 5: OCR/screenshot QA planning with `scripts/plan_ocr_qa.py`.
- Fixture smoke harness: offline Ren'Py fixture chain with `scripts/run_fixture_smoke.py`.
- Mock provider route: deterministic fixture provider with `scripts/run_mock_provider.py`.

## Paused Implementation Lines

These should be continued in a separate conversation:

- Real translation provider adapter.
- Local OCR adapter, likely RapidOCR or PaddleOCR first.
- Runtime screenshot capture automation.
- Paid cloud OCR or vision-model route behind budget approval.
- Godot packaged-game extraction/repacking strategy.

## Important Constraints To Preserve

- Do not modify Steam game folders during audit or sample generation.
- Keep output in separate directories.
- Keep provider/model/OCR calls disabled until dry-run estimates, pricing, budget, and explicit approval gates pass.
- Keep paid pricing external in user-owned config.
- Preserve `target_text` as the provider adapter output contract for `generate_patch.py`.
- Treat OCR as QA evidence, not final translation memory.
- Keep personal-use mode low-cost and reversible by default.

## Suggested Resume Order

1. Re-read `PROJECT_STATE.md`, `TODO.md`, and this file.
2. Pick one implementation line only.
3. If adding a new workflow or adapter, follow the skill's current intake -> design document -> prototype/brief gate first.
4. Implement the smallest adapter slice.
5. Run `scripts/run_fixture_smoke.py` before and after adapter work.
6. Verify against fixtures before any real game folder.

## Latest Implementation Note

`scripts/run_mock_provider.py` now fixes the `target_text` and `provider-usage-log.jsonl` contract for provider-like fixture tests. Real providers should follow the same output shape but replace deterministic mock usage with provider-reported usage where available.

## Current Thread Scope

The original thread was reserved for skill adjustments. Implementation work should still keep adapter slices small and fixture-verified before touching real game folders.
