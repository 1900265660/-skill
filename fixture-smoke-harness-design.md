# Fixture Smoke Harness Design

Date: 2026-06-28

## User Goal

Add a local regression harness for the existing `game-localization` safe workflow before adding provider, OCR, screenshot, paid vision, or Godot packaging adapters.

## Current Context

The skill already has separate scripts for:

- read-only audit
- inventory extraction
- inventory validation
- cost/provider dry-run planning
- sample translation package generation
- patch generation and static QA
- OCR QA planning

These scripts have been manually verified in previous phases, but there is no single command that proves the chain still works after future adapter changes.

## Non-Goals

- Do not call remote translation providers.
- Do not run real OCR engines.
- Do not launch games or capture screenshots.
- Do not unpack, repack, or patch real packaged games.
- Do not modify Steam game folders or fixture source folders.
- Do not solve Godot packaged-game extraction in this step.

## Proposed Workflow

Create `scripts/run_fixture_smoke.py`.

Default fixture:

- `assets/fixtures/renpy-small`

Default output:

- `generated-skill/smoke-output/renpy-small/<timestamp>`

The harness runs:

1. Compile current Python scripts.
2. `scan_project.py`
3. `extract_inventory.py`
4. `validate_inventory.py`
5. `estimate_cost.py` on `manual_csv`
6. `prepare_sample_translation.py` in `mock-zh` mode
7. `generate_patch.py`
8. `plan_ocr_qa.py`

Then it validates:

- Required artifacts exist.
- Source fixture file hashes are unchanged.
- Inventory has at least one row.
- Inventory validation has zero blockers.
- Cost gate is `READY_FOR_LOCAL_OR_MANUAL_STEP`.
- Sample inventory contains translated target text.
- Patch QA has zero blockers and at least one generated patch file.
- OCR planning gate is not blocked.

## Inputs And Outputs

Inputs:

- Fixture directory.
- Output directory.
- Target language and locale.
- Sample size.

Outputs:

- Full stage artifacts under the output directory.
- `fixture-smoke-report.json`
- `fixture-smoke-report.md`

## Safety And Rollback

- The harness rejects output directories inside the fixture.
- Existing output directories are not overwritten by default.
- Overwrite is allowed only for directories previously marked as harness-owned.
- Source fixture hashes are captured before and after the run.

## Cost Controls

- The harness uses only `manual_csv` and `mock-zh`.
- No remote provider, MCP, OCR, cloud OCR, or vision model call is made.

## QA Plan

Run the harness once after implementation.

Expected result:

- Exit code 0.
- Patch QA decision passes without blockers.
- Report files are generated.

Future adapters should run this harness before and after their own focused tests.

## Open Questions

- Whether to add more fixture profiles later for generic JSON, custom `.localization`, Unity `mission.txt`, and Godot package detection.
- Whether to wire the harness into a broader project test command once the skill becomes installable.

## Decision

Implement the Ren'Py fixture harness first because it covers the existing end-to-end sample patch path without package-tool, provider, OCR, or real-game risk.
