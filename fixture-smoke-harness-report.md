# Fixture Smoke Harness Report

Date: 2026-06-28

## Scope

Implemented a local offline smoke test harness for the `game-localization` skill.

The harness validates the current safe chain before future provider, OCR, screenshot, paid vision, or Godot package adapters are added.

## Files Added Or Updated

- Added `fixture-smoke-harness-design.md`
- Added `generated-skill/game-localization/scripts/run_fixture_smoke.py`
- Added `generated-skill/game-localization/references/verification-smoke-harness.md`
- Updated `generated-skill/game-localization/SKILL.md`
- Updated `translation-tool-handoff.md`
- Updated project tracking files: `PROJECT_STATE.md`, `TODO.md`, and `decisions.md`

## What The Harness Does

`run_fixture_smoke.py` runs the existing offline chain against the `renpy-small` fixture:

1. Python syntax compile.
2. Read-only audit.
3. Inventory extraction.
4. Inventory validation.
5. Manual cost dry-run.
6. Mock sample translation.
7. Patch generation and static QA.
8. OCR QA planning.

It then checks:

- Required artifacts exist.
- Fixture source file hashes are unchanged.
- Inventory has rows.
- Validation has zero blockers.
- Cost gate is ready for local/manual work.
- Sample target text is filled.
- Patch QA has zero blockers and at least one patch file.
- OCR planning is not blocked.

## Safety

- No remote provider, MCP, OCR engine, cloud OCR, or vision model is called.
- No game is launched.
- No Steam game folder is touched.
- Output directories are rejected if they are inside the fixture source folder.
- Existing output directories are not overwritten unless they were previously marked as harness-owned.

## Verification

Commands run:

```powershell
python "E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\game-localization\scripts\run_fixture_smoke.py" --out "E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\smoke-output\renpy-small\validation-run"
python "E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\game-localization\scripts\run_fixture_smoke.py" --out "E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\smoke-output\renpy-small\validation-run" --overwrite
```

Result:

- Decision: `PASS`
- Stages: 8 passed, 0 failed
- Assertions: 21 passed, 0 failed
- Inventory rows: 4
- Validation blockers: 0
- Cost gate: `READY_FOR_LOCAL_OR_MANUAL_STEP`
- Patch files: 1
- Patch QA blockers: 0
- OCR gate: `READY_FOR_LOCAL_OR_MANUAL_OCR`

Report output:

- `E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\smoke-output\renpy-small\validation-run\fixture-smoke-report.md`
- `E:\Projects\chanpin\skill-test-env\game-localization-skill\generated-skill\smoke-output\renpy-small\validation-run\fixture-smoke-report.json`

## Remaining Risks

- The harness currently covers the Ren'Py end-to-end sample path only.
- Generic JSON, Unity `mission.txt`, custom `.localization`/`.subtitles`, and Godot package fixtures are not yet included.
- It does not run real provider calls, OCR engines, screenshot capture, or game launches.

## Recommended Next Goal

Add provider usage log schema and a mock-provider execution route that consumes the existing budget/dry-run gates and writes `target_text`.
